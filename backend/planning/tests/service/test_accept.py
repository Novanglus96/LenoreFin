"""Accepting a plan rewrites the funding reminders; reverting restores them.

The forecast is patched out (`load_baselines`) so each test controls the
balance paths; everything else — buckets, reminders, rules — is real.
"""

from datetime import date, timedelta
from decimal import Decimal as D

import pytest

from planning.models import Bucket, PlanAcceptance, WindfallRule
from planning.services import accept as accept_mod
from planning.services import savings_plan as sp
from planning.services.accept import PlanError, accept_plan, revert_acceptance, snapshot
from reminders.models import Reminder, Repeat
from transactions.models import TransactionType

TODAY = date(2026, 12, 1)
FIRST = date(2027, 1, 1)


@pytest.fixture
def household(db, test_checking_account, test_savings_account, test_tag, bank, savings_account_type):
    biweekly = Repeat.objects.create(repeat_name="Every 2 Weeks (test)", weeks=2)
    income = TransactionType.objects.create(transaction_type="Income")
    transfer = TransactionType.objects.create(transaction_type="Transfer")
    Reminder.objects.create(
        tag=test_tag, amount=D("2000"), reminder_source_account=test_checking_account,
        description="Payroll", transaction_type=income, repeat=biweekly,
        start_date=date(2026, 12, 4), next_date=date(2026, 12, 4),
    )
    pet_reminder = Reminder.objects.create(
        tag=test_tag, amount=D("-60"), reminder_source_account=test_checking_account,
        reminder_destination_account=test_savings_account, description="Transfer to Pet",
        transaction_type=transfer, repeat=biweekly,
        start_date=date(2026, 12, 4), next_date=date(2026, 12, 4),
    )
    pet = Bucket.objects.create(
        name="Pet", contribution_per_paycheck=D("60"), account=test_savings_account,
        reminder=pet_reminder,
    )
    second = test_savings_account.__class__.objects.create(
        account_name="Vacation Savings", account_type=savings_account_type, bank=bank,
        opening_balance=0, open_date=TODAY,
    )
    return {
        "checking": test_checking_account, "pet": pet, "pet_reminder": pet_reminder,
        "second": second, "repeat": biweekly,
    }


@pytest.fixture
def flat_baselines(monkeypatch):
    """Every account starts at 5000 and nothing else happens: always solvent."""
    def fake(account_ids, today, end):
        return {a: sp.Baseline(a, D("5000"), []) for a in account_ids}
    monkeypatch.setattr(sp, "load_baselines", fake)


def reminders_state():
    return sorted(
        ({k: v for k, v in snapshot(r).items() if k != "id"} for r in Reminder.objects.all()),
        key=str,
    )


@pytest.mark.service
def test_accept_cuts_the_old_transfer_at_the_window_and_writes_the_new_one(household, flat_baselines):
    pet = household["pet"]
    acceptance = accept_plan(TODAY, edits={"buckets": {f"b{pet.pk}": {"per_paycheck": "80"}}})

    old = Reminder.objects.get(pk=household["pet_reminder"].pk)
    assert old.end_date == FIRST - timedelta(days=1)  # December still runs at 60
    pet.refresh_from_db()
    assert pet.contribution_per_paycheck == D("80")
    assert pet.reminder.amount == D("-80")
    assert pet.reminder.next_date == FIRST
    assert pet.reminder.end_date is None  # carries on past the window
    assert pet.reminder.repeat == household["repeat"]
    assert acceptance.buckets.get().action == "change"


@pytest.mark.service
def test_accepting_twice_changes_nothing_the_second_time(household, flat_baselines, monkeypatch):
    pet = household["pet"]
    edits = {"buckets": {f"b{pet.pk}": {"per_paycheck": "80"}}}
    accept_plan(TODAY, edits=edits)
    # The forecast would now show the new reminder's transfers: replay them.
    new = Bucket.objects.get(pk=pet.pk).reminder
    paydays = sp.pay_calendar(TODAY, date(2027, 12, 31), household["checking"].pk)
    rows = [(p, D("80"), new.pk) for p in paydays if p >= FIRST]

    def fake(account_ids, today, end):
        return {
            a: sp.Baseline(a, D("5000"), rows if a == pet.account_id else [])
            for a in account_ids
        }

    monkeypatch.setattr(sp, "load_baselines", fake)
    before = reminders_state()
    second = accept_plan(TODAY, edits=edits)
    assert second.buckets.count() == 0
    assert reminders_state() == before


@pytest.mark.service
def test_revert_puts_every_reminder_and_bucket_back(household, flat_baselines):
    pet = household["pet"]
    before = reminders_state()
    acceptance = accept_plan(TODAY, edits={"buckets": {f"b{pet.pk}": {"per_paycheck": "80", "goal_amount": "900"}}})
    revert_acceptance(acceptance, TODAY)
    assert reminders_state() == before
    pet.refresh_from_db()
    assert pet.contribution_per_paycheck == D("60")
    assert pet.goal_amount is None
    assert pet.reminder.description == "Transfer to Pet"
    assert PlanAcceptance.objects.get().reverted_on == TODAY


@pytest.mark.service
def test_a_reminder_with_nothing_left_before_the_window_is_deleted_and_restored(household, flat_baselines):
    reminder = household["pet_reminder"]
    reminder.next_date = date(2027, 1, 1)
    reminder.save()
    before = reminders_state()
    acceptance = accept_plan(TODAY, edits={"buckets": {f"b{household['pet'].pk}": {"per_paycheck": "70"}}})
    assert not Reminder.objects.filter(pk=reminder.pk).exists()
    revert_acceptance(acceptance, TODAY)
    assert reminders_state() == before
    assert Bucket.objects.get(name="Pet").reminder.description == "Transfer to Pet"


@pytest.mark.service
def test_new_and_removed_buckets(household, flat_baselines):
    pet = household["pet"]
    acceptance = accept_plan(
        TODAY,
        edits={
            "remove": [f"b{pet.pk}"],
            "new": [{"key": "new0", "name": "Vacation", "account_id": household["second"].pk, "per_paycheck": "100"}],
        },
    )
    vacation = Bucket.objects.get(name="Vacation")
    assert vacation.reminder.amount == D("-100")
    assert vacation.reminder.reminder_destination_account == household["second"]
    assert vacation.reminder.reminder_source_account == household["checking"]
    pet.refresh_from_db()
    assert pet.active is False
    assert Reminder.objects.get(pk=household["pet_reminder"].pk).end_date == FIRST - timedelta(days=1)

    revert_acceptance(acceptance, TODAY)
    assert not Bucket.objects.filter(name="Vacation").exists()
    pet.refresh_from_db()
    assert pet.active is True
    assert Reminder.objects.get(pk=household["pet_reminder"].pk).end_date is None


@pytest.mark.service
def test_reaching_a_goal_does_not_end_the_transfer(household, monkeypatch):
    # Pet starts at 0 and wants 120: reached after two transfers, but the plan
    # stands until the next review, so the reminder is not given an end date.
    pet_account = household["pet"].account_id
    paydays = sp.pay_calendar(TODAY, date(2027, 12, 31), household["checking"].pk)
    rows = [(p, D("60"), household["pet_reminder"].pk) for p in paydays]

    def fake(account_ids, today, end):
        return {
            a: sp.Baseline(a, D("0"), rows) if a == pet_account else sp.Baseline(a, D("5000"), [])
            for a in account_ids
        }
    monkeypatch.setattr(sp, "load_baselines", fake)
    accept_plan(TODAY, edits={"buckets": {f"b{household['pet'].pk}": {"goal_amount": "120"}}})
    pet = Bucket.objects.get(pk=household["pet"].pk)
    assert pet.goal_amount == D("120")
    assert pet.reminder.amount == D("-60")
    assert pet.reminder.end_date is None
    # The schedule did not change, so neither did the reminder.
    assert pet.reminder == household["pet_reminder"]


@pytest.mark.service
def test_accept_writes_the_overage_rules_and_revert_restores_them(household, flat_baselines):
    pet = household["pet"]
    WindfallRule.objects.create(rule="Money market first")  # a note: left alone
    acceptance = accept_plan(
        TODAY,
        edits={
            "buckets": {f"b{pet.pk}": {"goal_amount": "100000"}},
            "rules": [{"key": f"b{pet.pk}", "cap_amount": "250"}],
        },
    )
    rule = WindfallRule.objects.get(bucket=pet)
    assert rule.cap_amount == D("250")
    assert WindfallRule.objects.filter(rule="Money market first").exists()
    revert_acceptance(acceptance, TODAY)
    assert not WindfallRule.objects.filter(bucket__isnull=False).exists()
    assert WindfallRule.objects.filter(rule="Money market first").exists()


@pytest.mark.service
def test_an_insolvent_plan_cannot_be_accepted(household, monkeypatch):
    def fake(account_ids, today, end):
        return {a: sp.Baseline(a, D("-1"), []) for a in account_ids}
    monkeypatch.setattr(sp, "load_baselines", fake)
    with pytest.raises(PlanError):
        accept_plan(TODAY)
    assert not PlanAcceptance.objects.exists()


@pytest.mark.service
def test_an_insolvent_plan_can_be_accepted_deliberately(household, monkeypatch):
    def fake(account_ids, today, end):
        return {a: sp.Baseline(a, D("-1"), []) for a in account_ids}
    monkeypatch.setattr(sp, "load_baselines", fake)
    pet = household["pet"]
    acceptance = accept_plan(
        TODAY, edits={"buckets": {f"b{pet.pk}": {"per_paycheck": "80"}}}, force=True
    )
    assert acceptance.verdict == "insolvent"
    pet.refresh_from_db()
    assert pet.reminder.amount == D("-80")


@pytest.mark.service
def test_only_the_latest_standing_plan_can_be_undone(household, flat_baselines):
    pet = household["pet"]
    first = accept_plan(TODAY, edits={"buckets": {f"b{pet.pk}": {"per_paycheck": "70"}}})
    accept_plan(TODAY, edits={"buckets": {f"b{pet.pk}": {"per_paycheck": "90"}}})
    with pytest.raises(PlanError):
        revert_acceptance(first, TODAY)


@pytest.mark.service
def test_imported_plans_cannot_be_undone(household):
    imported = PlanAcceptance.objects.create(
        accepted_on=TODAY, window_start=FIRST, window_end=date(2027, 12, 31),
        total_per_paycheck=D("60"), imported=True,
    )
    with pytest.raises(PlanError):
        accept_mod.revert_acceptance(imported, TODAY)
