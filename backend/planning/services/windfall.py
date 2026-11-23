"""Windfalls: money arriving outside the pay calendar.

You type the amount; the rules suggest where it goes; you accept the split or
edit it; applying writes one pending transfer per bucket.

First, every bucket that is not solvent under the current plan is made whole:
it gets what lifts its lowest projected balance back to zero, the earliest
trouble first. A hole comes before any goal.

Then the suggestion walks the windfall rules that name a bucket, in order. Each
takes the smaller of what is left and what it wants:

- its `cap_amount`, when one is set;
- otherwise its bucket's shortfall against its goal under the current plan;
- otherwise (no cap, no goal) everything that is left — a "remainder to X"
  rule, which is how these rules have always been written.

Rules with no bucket are notes, shown alongside, never computed on.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db import transaction as db_transaction

from planning.models import Bucket, WindfallAllocation, WindfallApplication, WindfallRule
from planning.services.savings_plan import build_plan

CENT = Decimal("0.01")
ZERO = Decimal("0.00")


class WindfallError(Exception):
    pass


def suggest(amount: Decimal, today: date) -> dict:
    amount = Decimal(str(amount)).quantize(CENT)
    plan = build_plan(today)
    lines = {b["bucket_id"]: b for b in plan.get("buckets", []) if b.get("bucket_id")}
    buckets = {
        b.pk: b
        for b in Bucket.objects.filter(active=True, account__isnull=False).select_related(
            "account"
        )
    }
    left = amount
    rows: dict[int, dict] = {}

    def give(bucket: Bucket, wants: Decimal, why: str, rule: str | None) -> None:
        nonlocal left
        wants = max(ZERO, Decimal(str(wants))).quantize(CENT)
        share = min(left, wants)
        row = rows.get(bucket.pk)
        if row is None:
            row = rows[bucket.pk] = {
                "bucket_id": bucket.pk,
                "name": bucket.name,
                "account_id": bucket.account_id,
                "account_name": bucket.account.account_name,
                "wants": ZERO,
                "why": why,
                "suggested": ZERO,
                "rule": rule,
            }
        else:
            row["why"] = f"{row['why']}; {why}"
        row["wants"] += wants
        row["suggested"] += share
        left -= share

    # 1. Holes first: buckets that are not solvent, earliest trouble first.
    insolvent = sorted(
        (b for b in lines.values() if b.get("verdict") == "insolvent" and b["bucket_id"] in buckets),
        key=lambda b: (b["dips"][0]["start"] if b.get("dips") else b["low_when"]),
    )
    for line in insolvent:
        need = -Decimal(str(line["low_balance"]))
        give(
            buckets[line["bucket_id"]],
            need,
            f"not solvent — lowest {line['low_balance']} on {line['low_when']}",
            None,
        )

    # 2. Then the order the household set.
    for rule in WindfallRule.objects.filter(bucket__isnull=False):
        bucket = buckets.get(rule.bucket_id)
        if bucket is None:
            continue
        already = rows[bucket.pk]["suggested"] if bucket.pk in rows else ZERO
        line = lines.get(bucket.pk, {})
        if rule.cap_amount is not None:
            wants, why = rule.cap_amount, f"rule cap {rule.cap_amount}"
        elif line.get("shortfall") is not None:
            # What a solvency top-up already put in counts toward the goal.
            wants = max(ZERO, Decimal(str(line["shortfall"])) - already)
            why = (
                f"{line['shortfall']} short of its goal"
                if Decimal(str(line["shortfall"])) > 0
                else "goal already met by its date"
            )
        else:
            wants, why = left, "takes the remainder"
        give(bucket, wants, why, rule.rule)

    notes = list(
        WindfallRule.objects.filter(bucket__isnull=True).values("rule", "cap", "order")
    )
    return {
        "amount": amount,
        "allocations": list(rows.values()),
        "unallocated": left.quantize(CENT),
        "notes": notes,
    }


def _invalidate(account_ids) -> None:
    from accounts.models import Account
    from core.cache.helpers import delete_pattern
    from core.cache.keys import account_all

    ids = {a for a in account_ids if a}
    parents = set(
        Account.objects.filter(id__in=ids, parent_account_id__isnull=False).values_list(
            "parent_account_id", flat=True
        )
    )
    for account_id in ids | parents:
        delete_pattern(account_all(account_id))


@db_transaction.atomic
def apply(
    amount: Decimal,
    arrival_date: date,
    source_account_id: int,
    allocations: list[dict],
    today: date,
    memo: str | None = None,
) -> WindfallApplication:
    """Write the split the owner settled on: one pending transfer per bucket.

    `allocations` = [{"bucket_id": 3, "amount": "500.00", "suggested": "450"}].
    The split is the owner's, not recomputed: the suggestion was only that.
    """
    from transactions.models import (
        Transaction,
        TransactionDetail,
        TransactionStatus,
        TransactionType,
    )

    amount = Decimal(str(amount)).quantize(CENT)
    shares = [
        (a, Decimal(str(a.get("amount") or 0)).quantize(CENT)) for a in allocations
    ]
    shares = [(a, s) for a, s in shares if s > 0]
    if any(s < 0 for _, s in shares):
        raise WindfallError("A share cannot be negative.")
    total = sum((s for _, s in shares), ZERO)
    if total > amount:
        raise WindfallError(f"The split ({total}) is more than the windfall ({amount}).")
    buckets = {
        b.pk: b
        for b in Bucket.objects.filter(pk__in=[a["bucket_id"] for a, _ in shares])
        .select_related("reminder")
    }
    for a, _ in shares:
        bucket = buckets.get(a["bucket_id"])
        if bucket is None or not bucket.account_id:
            raise WindfallError("Every share needs a bucket with an account.")

    application = WindfallApplication.objects.create(
        applied_on=today,
        arrival_date=arrival_date,
        amount=amount,
        allocated=total,
        source_account_id=source_account_id,
    )
    transfer_type_id = TransactionType.objects.values_list("id", flat=True).get(
        slug="transfer"
    )
    pending_id = TransactionStatus.objects.values_list("id", flat=True).get(
        slug="pending"
    )
    touched = {source_account_id}
    for a, share in shares:
        bucket = buckets[a["bucket_id"]]
        # Stored negative: for a transfer the sign is the direction, and the
        # destination reads the absolute value.
        transfer = Transaction.objects.create(
            transaction_date=arrival_date,
            total_amount=-share,
            status_id=pending_id,
            memo=memo,
            description=f"Windfall to {bucket.name}",
            edit_date=today,
            add_date=today,
            transaction_type_id=transfer_type_id,
            source_account_id=source_account_id,
            destination_account_id=bucket.account_id,
        )
        tag_id = bucket.reminder.tag_id if bucket.reminder_id else None
        if tag_id:
            TransactionDetail.objects.create(
                transaction=transfer, detail_amt=-share, tag_id=tag_id, full_toggle=True
            )
        touched.add(bucket.account_id)
        WindfallAllocation.objects.create(
            application=application,
            bucket=bucket,
            bucket_name=bucket.name,
            amount=share,
            suggested=Decimal(str(a.get("suggested") or 0)).quantize(CENT),
            transaction=transfer,
        )
    db_transaction.on_commit(lambda: _invalidate(touched))
    return application


@db_transaction.atomic
def revert(application: WindfallApplication, today: date) -> WindfallApplication:
    """Delete the transfers a windfall wrote; keep the record, marked undone."""
    from transactions.models import Transaction

    if application.reverted_on is not None:
        raise WindfallError("That windfall has already been undone.")
    ids = [a.transaction_id for a in application.allocations.all() if a.transaction_id]
    touched = {application.source_account_id}
    for row in Transaction.objects.filter(pk__in=ids):
        touched |= {row.source_account_id, row.destination_account_id}
        row.delete()
    application.reverted_on = today
    application.save(update_fields=["reverted_on"])
    db_transaction.on_commit(lambda: _invalidate(touched))
    return application
