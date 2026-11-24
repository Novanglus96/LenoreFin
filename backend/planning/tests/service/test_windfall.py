from datetime import date
from decimal import Decimal as D

import pytest

from planning.models import Bucket, WindfallApplication, WindfallRule
from planning.services import savings_plan as sp
from planning.services import windfall
from reminders.models import Reminder, Repeat
from transactions.models import Transaction, TransactionStatus, TransactionType

TODAY = date(2026, 12, 1)


@pytest.fixture
def setup(db, test_checking_account, test_savings_account, test_tag, bank, savings_account_type, monkeypatch):
    TransactionStatus.objects.create(transaction_status="Pending")
    biweekly = Repeat.objects.create(repeat_name="Every 2 Weeks (test)", weeks=2)
    TransactionType.objects.create(transaction_type="Income")
    transfer = TransactionType.objects.create(transaction_type="Transfer")
    Reminder.objects.create(
        tag=test_tag, amount=D("2000"), reminder_source_account=test_checking_account,
        description="Payroll", transaction_type=TransactionType.objects.get(transaction_type="Income"),
        repeat=biweekly, start_date=date(2026, 12, 4), next_date=date(2026, 12, 4),
    )
    car_account = test_savings_account.__class__.objects.create(
        account_name="Car", account_type=savings_account_type, bank=bank, opening_balance=0, open_date=TODAY,
    )
    car_reminder = Reminder.objects.create(
        tag=test_tag, amount=D("-50"), reminder_source_account=test_checking_account,
        reminder_destination_account=car_account, description="Transfer to Car",
        transaction_type=transfer, repeat=biweekly, start_date=date(2026, 12, 4), next_date=date(2026, 12, 4),
    )
    # Car is 1000 short of its goal; Vacation has no goal and takes the rest.
    car = Bucket.objects.create(name="Car", contribution_per_paycheck=0, goal_amount=D("1000"),
                                account=car_account, reminder=car_reminder)
    vacation = Bucket.objects.create(name="Vacation", contribution_per_paycheck=0, account=test_savings_account)
    WindfallRule.objects.create(rule="Fill the car", bucket=car, order=1)
    WindfallRule.objects.create(rule="Remainder to Vacation", bucket=vacation, order=2)
    WindfallRule.objects.create(rule="Money market first", order=0)

    def fake(account_ids, today, end):
        return {a: sp.Baseline(a, D("0") if a == car_account.pk else D("5000"), []) for a in account_ids}

    monkeypatch.setattr(sp, "load_baselines", fake)
    return {"car": car, "vacation": vacation, "checking": test_checking_account}


@pytest.mark.service
def test_suggest_walks_the_rules(setup):
    result = windfall.suggest(D("1500"), TODAY)
    split = {r["name"]: r["suggested"] for r in result["allocations"]}
    assert split == {"Car": D("1000.00"), "Vacation": D("500.00")}
    assert result["unallocated"] == D("0.00")
    assert [n["rule"] for n in result["notes"]] == ["Money market first"]


@pytest.mark.service
def test_a_cap_overrides_the_shortfall(setup):
    WindfallRule.objects.filter(bucket=setup["car"]).update(cap_amount=D("300"))
    split = {r["name"]: r["suggested"] for r in windfall.suggest(D("500"), TODAY)["allocations"]}
    assert split == {"Car": D("300.00"), "Vacation": D("200.00")}


@pytest.mark.service
def test_apply_writes_the_edited_split_as_pending_transfers_and_revert_deletes_them(setup):
    application = windfall.apply(
        D("1500"), date(2026, 12, 12), setup["checking"].pk,
        [{"bucket_id": setup["car"].pk, "amount": "700", "suggested": "1000"},
         {"bucket_id": setup["vacation"].pk, "amount": "0"}],
        TODAY,
    )
    assert application.allocated == D("700.00")
    transfer = Transaction.objects.get(description="Windfall to Car")
    assert transfer.total_amount == D("-700.00")
    assert transfer.destination_account == setup["car"].account
    assert transfer.status.transaction_status == "Pending"
    assert transfer.transaction_date == date(2026, 12, 12)
    assert not Transaction.objects.filter(description="Windfall to Vacation").exists()

    windfall.revert(application, TODAY)
    assert not Transaction.objects.filter(description__startswith="Windfall").exists()
    assert WindfallApplication.objects.get().reverted_on == TODAY


@pytest.mark.service
def test_a_split_larger_than_the_windfall_is_refused(setup):
    with pytest.raises(windfall.WindfallError):
        windfall.apply(D("100"), TODAY, setup["checking"].pk,
                       [{"bucket_id": setup["car"].pk, "amount": "150"}], TODAY)
    assert not WindfallApplication.objects.exists()


@pytest.mark.service
def test_a_bucket_that_is_not_solvent_is_made_whole_before_any_rule(setup, monkeypatch, test_savings_account):
    # Vacation's account dips to -300 the day after the first paycheck and
    # never recovers on 0 a paycheck: not solvent, so it is filled first.
    car_account = setup["car"].account_id

    def fake(account_ids, today, end):
        out = {}
        for a in account_ids:
            if a == test_savings_account.pk:
                out[a] = sp.Baseline(a, D("0"), [(date(2027, 1, 2), D("-300"), None)])
            else:
                out[a] = sp.Baseline(a, D("0") if a == car_account else D("5000"), [])
        return out

    monkeypatch.setattr(sp, "load_baselines", fake)
    result = windfall.suggest(D("1000"), TODAY)
    rows = result["allocations"]
    assert rows[0]["name"] == "Vacation"
    assert rows[0]["why"].startswith("not solvent")
    # 300 to Vacation's hole, then Car's 1000 goal takes the remaining 700.
    split = {r["name"]: r["suggested"] for r in rows}
    assert split == {"Vacation": D("300.00"), "Car": D("700.00")}
