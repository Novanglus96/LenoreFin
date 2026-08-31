"""Which rows the plan lifts off an account before it superimposes itself.

`baseline_path` removes the transfers the plan is *deciding* so a rate is
solved against an account nobody is funding yet. Getting the predicate wrong
does not raise: it silently leaves the funding on the path, so the account
looks like it already has what it needs and every requirement collapses.

The predicate is the reminder id rather than the reminder's description, and
that is the whole point of these tests. Applying a plan is expected to rename
transfers to a convention, and a name-based exclusion would stop matching at
exactly that moment.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from planning.services.savings_plan import baseline_path

TODAY = date(2026, 1, 1)
END = TODAY + timedelta(days=30)


def row(day, balance, description, reminder_id=None):
    """One forecast row in the shape `baseline_path` reads them."""
    return {
        "transaction_date": TODAY + timedelta(days=day),
        "balance": Decimal(str(balance)),
        "description": description,
        "reminder_id": reminder_id,
        "source_account_id": None,
        "destination_account_id": None,
    }


@pytest.fixture
def rows(monkeypatch):
    """Patch the forecast so these tests are about the predicate, not the ledger."""
    captured = {}

    def fake(end_date, account_id, totals_only, forecast, start_date, cleared_only):
        return captured["rows"], captured["opening"]

    monkeypatch.setattr(
        "planning.services.savings_plan.get_account_transactions_and_balances", fake
    )

    def use(rows, opening=Decimal("100")):
        captured["rows"] = rows
        captured["opening"] = opening

    return use


@pytest.mark.service
def test_the_excluded_transfer_is_backed_out_of_every_later_point(rows):
    """Its delta is removed from the running balance, not merely skipped.

    Skipping the row alone would leave every later balance still carrying the
    transfer, which is the bug this backing-out exists to prevent.
    """
    rows([
        row(1, 200, "Transfer to Vacation", reminder_id=7),   # +100, excluded
        row(2, 250, "Groceries"),                             # +50, kept
    ])
    path, _ = baseline_path(1, TODAY, END, {7})

    # Opening 100, the +100 transfer lifted out, then the +50 that stays.
    assert [p.balance for p in path if p.day in (1, 2)] == [
        Decimal("100.00"),
        Decimal("150.00"),
    ]


@pytest.mark.service
def test_renaming_the_reminder_does_not_stop_it_being_excluded(rows):
    """The trap this predicate exists to close.

    Applying a plan renames transfers to a naming convention. Under a
    description match the renamed row would sail through, the funding would be
    counted twice, and the account would report needing nothing.
    """
    renamed = [
        row(1, 200, "Auto: Vacation (savings plan)", reminder_id=7),
        row(2, 250, "Groceries"),
    ]
    rows(renamed)
    path, _ = baseline_path(1, TODAY, END, {7})

    assert [p.balance for p in path if p.day in (1, 2)] == [
        Decimal("100.00"),
        Decimal("150.00"),
    ]


@pytest.mark.service
def test_a_transfer_sharing_a_name_but_not_the_reminder_is_kept(rows):
    """The converse: a name collision must not delete real money.

    A one-off the household entered by hand carries no reminder, so it is
    money that genuinely moves and belongs on the path however it is labelled.
    """
    rows([
        row(1, 200, "Transfer to Vacation", reminder_id=7),   # the plan's own
        row(2, 300, "Transfer to Vacation", reminder_id=None),  # a real one-off
    ])
    path, _ = baseline_path(1, TODAY, END, {7})

    assert [p.balance for p in path if p.day in (1, 2)] == [
        Decimal("100.00"),
        Decimal("200.00"),
    ]


@pytest.mark.service
def test_an_excluded_row_still_contributes_a_point(rows):
    """Zero delta, but the date is still on the path.

    Dropping it outright collapses the path to a single entry for any bucket
    whose only modelled flow is the transfer being planned, and a one-point
    path can never show drift accumulating.
    """
    rows([row(5, 200, "Transfer to Vacation", reminder_id=7)])
    path, _ = baseline_path(1, TODAY, END, {7})

    assert [p.day for p in path] == [0, 5, 30]
    assert {p.balance for p in path} == {Decimal("100.00")}
