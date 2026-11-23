"""Accepting a savings plan: rewrite the funding reminders, and undo it.

A plan is a schedule per bucket — the planned amount on every transfer of the
window. Accepting makes the reminders say exactly that, from the first
transfer of the window on:

1. Every reminder the bucket's funding already uses is cut back to end the day
   before the window's first transfer. One that has nothing left to do before
   then is deleted. Either way its prior state is snapshotted.
2. A fresh reminder is written for each run with money in it. The last run
   stays open-ended, so the plan's final amount carries past the window.
3. The bucket's own figures (amount, goal, active) are written, new buckets
   are created, removed buckets are switched off.
4. The bucket-linked windfall rules are replaced by the plan's overage order.

Unchanged buckets are left alone, so accept → re-plan → accept is a no-op.
Everything is recorded on a `PlanAcceptance`, and revert puts it all back.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction

from planning.models import AcceptedBucket, Bucket, PlanAcceptance, WindfallRule
from planning.services.savings_plan import (
    INSOLVENT,
    PlanEntry,
    apply_edits,
    entries_from_buckets,
    funding_account_id,
    pay_repeat_id,
    resolve_window,
    simulate,
)
from reminders.models import Reminder
from transactions.models import TransactionType

REMINDER_FIELDS = [
    "tag_id",
    "amount",
    "reminder_source_account_id",
    "reminder_destination_account_id",
    "description",
    "transaction_type_id",
    "start_date",
    "next_date",
    "end_date",
    "repeat_id",
    "auto_add",
    "memo",
]
_DATES = {"start_date", "next_date", "end_date"}


class PlanError(Exception):
    pass


def snapshot(reminder: Reminder) -> dict:
    data = {"id": reminder.pk}
    for name in REMINDER_FIELDS:
        value = getattr(reminder, name)
        if isinstance(value, date):
            value = value.isoformat()
        elif isinstance(value, Decimal):
            value = str(value)
        data[name] = value
    return data


def _restore(data: dict) -> Reminder:
    fields = {
        k: (date.fromisoformat(v) if k in _DATES and v else v)
        for k, v in data.items()
        if k in REMINDER_FIELDS
    }
    existing = Reminder.objects.filter(pk=data["id"]).first()
    if existing is None:
        return Reminder.objects.create(**fields)
    for k, v in fields.items():
        setattr(existing, k, v)
    existing.save()
    return existing


def _template(managed_ids: set[int]) -> Reminder | None:
    """A funding reminder to copy tag, type and auto-add from."""
    return (
        Reminder.objects.filter(pk__in=managed_ids).order_by("-id").first()
        or Reminder.objects.filter(
            buckets__isnull=False, transaction_type__slug="transfer"
        )
        .order_by("-id")
        .first()
    )


def _write_runs(
    segments: list[dict],
    template: Reminder | None,
    funding_id: int,
    account_id: int,
    name: str,
    repeat_id: int | None,
) -> list[Reminder]:
    paid = [s for s in segments if s["amount"] > 0]
    if not paid:
        return []
    if template is None:
        raise PlanError(
            "No existing funding transfer to copy a tag from; link one bucket "
            "to its transfer first."
        )
    last_run = segments[-1]
    transfer_type = TransactionType.objects.filter(slug="transfer").first()
    created = []
    for run in paid:
        open_ended = run is last_run
        created.append(
            Reminder.objects.create(
                tag_id=template.tag_id,
                amount=-run["amount"],
                reminder_source_account_id=funding_id,
                reminder_destination_account_id=account_id,
                description=template.description
                if template.reminder_destination_account_id == account_id
                else f"Transfer to {name}",
                transaction_type=transfer_type or template.transaction_type,
                start_date=run["start"],
                next_date=run["start"],
                end_date=None if open_ended else run["end"],
                repeat_id=repeat_id or template.repeat_id,
                auto_add=template.auto_add,
                memo=template.memo,
            )
        )
    return created


def _trim(managed_ids: set[int], first_transfer: date) -> list[dict]:
    """End every managed reminder before the window; delete idle ones."""
    snapshots = []
    cutoff = first_transfer - timedelta(days=1)
    for reminder in Reminder.objects.filter(pk__in=managed_ids):
        if reminder.end_date is not None and reminder.end_date < first_transfer:
            continue
        snapshots.append(snapshot(reminder))
        if reminder.next_date is None or reminder.next_date >= first_transfer:
            reminder.delete()
        else:
            reminder.end_date = cutoff
            reminder.save()
    return snapshots


def _refresh_caches(reminder_ids: list[int]) -> None:
    """Rebuild the reminder caches now, so the next plan read sees them.

    The save signal queues the same rebuild on the worker; doing it inline as
    well means the page does not show the old schedule for a few seconds.
    """
    from transactions.tasks import update_reminder_cache

    for rid in reminder_ids:
        if Reminder.objects.filter(pk=rid).exists():
            update_reminder_cache(rid)


def _rules_snapshot() -> list[dict]:
    return [
        {
            "rule": r.rule,
            "cap": r.cap,
            "cap_amount": str(r.cap_amount) if r.cap_amount is not None else None,
            "order": r.order,
            "bucket_id": r.bucket_id,
        }
        for r in WindfallRule.objects.filter(bucket__isnull=False)
    ]


def _write_rules(rules: list[dict], keys_to_bucket: dict[str, Bucket]) -> None:
    WindfallRule.objects.filter(bucket__isnull=False).delete()
    base = (
        max(WindfallRule.objects.values_list("order", flat=True), default=0) + 1
    )
    for i, rule in enumerate(rules):
        bucket = keys_to_bucket.get(rule["key"])
        if bucket is None:
            continue
        cap = rule.get("cap_amount")
        WindfallRule.objects.update_or_create(
            rule=f"Top up {bucket.name}",
            defaults={
                "bucket": bucket,
                "cap_amount": Decimal(str(cap)) if cap not in (None, "") else None,
                "order": base + i,
            },
        )


@transaction.atomic
def accept_plan(
    today: date,
    start: date | None = None,
    end: date | None = None,
    edits: dict | None = None,
    force: bool = False,
) -> PlanAcceptance:
    """Write the plan. An insolvent plan needs `force` — the owner's override."""
    funding_id = funding_account_id()
    if funding_id is None:
        raise PlanError("No funding account: link a bucket to its transfer first.")
    window = resolve_window(today, funding_id, start, end)
    entries: list[PlanEntry] = apply_edits(entries_from_buckets(), edits)
    plan = simulate(today, window, entries, (edits or {}).get("overage_order"))
    if plan["verdict"] == INSOLVENT and not force:
        raise PlanError(
            "This plan is not solvent. Accept it anyway to override."
        )

    first_transfer = plan["window"]["first_transfer"]
    repeat_id = pay_repeat_id(funding_id)
    by_key = {e.key: e for e in entries}
    acceptance = PlanAcceptance.objects.create(
        accepted_on=today,
        window_start=window.start,
        window_end=window.end,
        total_per_paycheck=plan["total_planned_per_paycheck"],
        verdict=plan["verdict"],
        rules_snapshot=_rules_snapshot(),
    )
    keys_to_bucket: dict[str, Bucket] = {}
    touched: list[int] = []

    for row in plan["buckets"]:
        entry = by_key[row["key"]]
        bucket = entry.bucket

        if entry.remove:
            snaps = _trim(entry.managed, first_transfer)
            AcceptedBucket.objects.create(
                acceptance=acceptance,
                bucket=bucket,
                bucket_name=bucket.name,
                action=AcceptedBucket.ACTION_REMOVE,
                per_paycheck=Decimal("0"),
                previous_per_paycheck=bucket.contribution_per_paycheck,
                previous_goal_amount=bucket.goal_amount,
                previous_goal_date=bucket.goal_date,
                previous_active=bucket.active,
                previous_reminder_id=bucket.reminder_id,
                reminder_snapshots=snaps,
            )
            bucket.active = False
            bucket.save(update_fields=["active"])
            touched += [s["id"] for s in snaps]
            continue

        if not entry.account_id:
            continue

        if bucket is None:
            bucket = Bucket.objects.create(
                name=entry.name,
                account_id=entry.account_id,
                contribution_per_paycheck=entry.per_paycheck,
                goal_amount=entry.goal_amount,
                goal_date=entry.goal_date,
            )
            created = _write_runs(
                row["segments"], _template(set()), funding_id,
                entry.account_id, entry.name, repeat_id,
            )
            record = AcceptedBucket.objects.create(
                acceptance=acceptance,
                bucket=bucket,
                bucket_name=bucket.name,
                action=AcceptedBucket.ACTION_CREATE,
                per_paycheck=entry.per_paycheck,
            )
            record.created_reminders.set(created)
            if created:
                bucket.reminder = created[-1]
                bucket.save(update_fields=["reminder"])
            keys_to_bucket[entry.key] = bucket
            touched += [r.pk for r in created]
            continue

        keys_to_bucket[entry.key] = bucket
        fields_changed = (
            bucket.contribution_per_paycheck != entry.per_paycheck
            or bucket.goal_amount != entry.goal_amount
            or bucket.goal_date != entry.goal_date
        )
        if not row["changed"] and not fields_changed:
            continue

        record = AcceptedBucket.objects.create(
            acceptance=acceptance,
            bucket=bucket,
            bucket_name=bucket.name,
            action=AcceptedBucket.ACTION_CHANGE,
            per_paycheck=entry.per_paycheck,
            previous_per_paycheck=bucket.contribution_per_paycheck,
            previous_goal_amount=bucket.goal_amount,
            previous_goal_date=bucket.goal_date,
            previous_active=bucket.active,
            previous_reminder_id=bucket.reminder_id,
        )
        if row["changed"]:
            template = _template(entry.managed)
            snaps = _trim(entry.managed, first_transfer)
            created = _write_runs(
                row["segments"], template, funding_id,
                entry.account_id, bucket.name, repeat_id,
            )
            record.reminder_snapshots = snaps
            record.save(update_fields=["reminder_snapshots"])
            record.created_reminders.set(created)
            if created:
                bucket.reminder = created[-1]
            touched += [s["id"] for s in snaps] + [r.pk for r in created]
        bucket.contribution_per_paycheck = entry.per_paycheck
        bucket.goal_amount = entry.goal_amount
        bucket.goal_date = entry.goal_date
        bucket.save()

    # A rule with no cap takes its bucket's shortfall as it stands when the
    # windfall arrives — calculated, not frozen at today's figure. Only a cap
    # the owner typed is stored.
    rules = (edits or {}).get("rules")
    if rules is None:
        rules = [{"key": r["key"], "cap_amount": None} for r in plan["suggested_rules"]]
    _write_rules(rules, keys_to_bucket)

    transaction.on_commit(lambda: _refresh_caches(touched))
    return acceptance


def last_acceptance() -> PlanAcceptance | None:
    return PlanAcceptance.objects.filter(reverted_on__isnull=True).first()


@transaction.atomic
def revert_acceptance(acceptance: PlanAcceptance, today: date) -> PlanAcceptance:
    if acceptance.reverted_on is not None:
        raise PlanError("That plan has already been undone.")
    if acceptance.imported:
        raise PlanError("A plan restored from a backup cannot be undone.")
    latest = last_acceptance()
    if latest is None or latest.pk != acceptance.pk:
        raise PlanError("Only the most recently accepted plan can be undone.")

    touched: list[int] = []
    for record in acceptance.buckets.all():
        created_ids = list(record.created_reminders.values_list("pk", flat=True))
        Reminder.objects.filter(pk__in=created_ids).delete()
        restored = {s["id"]: _restore(s) for s in record.reminder_snapshots}
        touched += [r.pk for r in restored.values()]
        bucket = record.bucket
        if bucket is None:
            continue
        if record.action == AcceptedBucket.ACTION_CREATE:
            bucket.delete()
            continue
        bucket.contribution_per_paycheck = record.previous_per_paycheck
        bucket.goal_amount = record.previous_goal_amount
        bucket.goal_date = record.previous_goal_date
        bucket.active = record.previous_active
        previous = record.previous_reminder_id
        if previous in restored:
            bucket.reminder = restored[previous]
        elif previous and Reminder.objects.filter(pk=previous).exists():
            bucket.reminder_id = previous
        bucket.save()

    WindfallRule.objects.filter(bucket__isnull=False).delete()
    for rule in acceptance.rules_snapshot:
        if Bucket.objects.filter(pk=rule["bucket_id"]).exists():
            WindfallRule.objects.update_or_create(
                rule=rule["rule"],
                defaults={
                    "bucket_id": rule["bucket_id"],
                    "cap": rule["cap"],
                    "cap_amount": rule["cap_amount"],
                    "order": rule["order"],
                },
            )

    acceptance.reverted_on = today
    acceptance.save(update_fields=["reverted_on"])
    transaction.on_commit(lambda: _refresh_caches(touched))
    return acceptance
