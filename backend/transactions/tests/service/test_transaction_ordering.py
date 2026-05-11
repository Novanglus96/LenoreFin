"""
Tests for transaction ordering, balance accumulation, and the forecast path.

These are critical: incorrect sort order or balance threading breaks every
account view and forecast in the app.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from transactions.models import Transaction, ReminderCacheTransaction, ForecastCacheTransaction
from transactions.api.dependencies.transaction_utilities import (
    sort_transaction_list,
    add_balances_to_transaction_list,
    annotate_transaction_total,
)
from transactions.api.dependencies.get_transactions_by_account import (
    get_transactions_by_account,
)

AUTH = {"Authorization": "Bearer test-api-key"}

TODAY = date(2026, 6, 1)


# ---------------------------------------------------------------------------
# Cache isolation — LocMemCache persists across tests within a session.
# get_transactions_by_account caches by account_id; SQLite rolls back rows but
# sequences reset too, so the same account can get the same ID in every test.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()
YESTERDAY = TODAY - timedelta(days=1)
TOMORROW = TODAY + timedelta(days=1)
NEXT_WEEK = TODAY + timedelta(days=7)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_stub(id, status_slug, transaction_date, pretty_total):
    """Build a minimal TransactionOut-like object for list-sort tests."""
    from unittest.mock import MagicMock
    t = MagicMock()
    t.id = id
    t.transaction_date = transaction_date
    t.pretty_total = Decimal(str(pretty_total))
    t.balance = Decimal("0")
    t.status = MagicMock()
    t.status.slug = status_slug
    t.status.id = {"pending": 2, "cleared": 0, "reconciled": 0}.get(status_slug, 1)
    # Not a dict — exercises the object branch
    t.__class__ = object
    return t


def _make_dict(id, status_slug, transaction_date, pretty_total):
    """Build a minimal dict for list-sort tests — exercises the dict branch."""
    from unittest.mock import MagicMock
    status = MagicMock()
    status.slug = status_slug
    status.id = {"pending": 2, "cleared": 0, "reconciled": 0}.get(status_slug, 1)
    return {
        "id": id,
        "transaction_date": transaction_date,
        "pretty_total": Decimal(str(pretty_total)),
        "balance": Decimal("0"),
        "status": status,
    }


# ---------------------------------------------------------------------------
# sort_transaction_list — object path
# ---------------------------------------------------------------------------

@pytest.mark.service
def test_sort_pending_after_cleared_objects():
    """Pending transactions sort after cleared ones on the same date."""
    cleared = _make_stub(1, "cleared", TODAY, -10)
    pending = _make_stub(2, "pending", TODAY, -10)

    result = sort_transaction_list([pending, cleared])
    assert result[0].id == 1  # cleared first
    assert result[1].id == 2  # pending last


@pytest.mark.service
def test_sort_by_date_ascending_objects():
    """Earlier dates sort before later dates within the same priority."""
    t1 = _make_stub(1, "pending", TOMORROW, -10)
    t2 = _make_stub(2, "pending", TODAY, -10)

    result = sort_transaction_list([t1, t2])
    assert result[0].transaction_date == TODAY
    assert result[1].transaction_date == TOMORROW


@pytest.mark.service
def test_sort_same_date_larger_amount_first_objects():
    """On the same date and priority, smaller absolute expense sorts first.
    Sort key is -pretty_total ascending: -(-5)=5 < -(-50)=50, so small comes first."""
    small = _make_stub(1, "pending", TODAY, -5)
    large = _make_stub(2, "pending", TODAY, -50)

    result = sort_transaction_list([small, large])
    assert result[0].id == 1   # -(-5)=5 sorts before -(-50)=50
    assert result[1].id == 2


@pytest.mark.service
def test_sort_same_date_same_amount_higher_id_first_objects():
    """Tiebreak: higher id sorts first."""
    t1 = _make_stub(1, "pending", TODAY, -10)
    t2 = _make_stub(5, "pending", TODAY, -10)

    result = sort_transaction_list([t1, t2])
    assert result[0].id == 5
    assert result[1].id == 1


# ---------------------------------------------------------------------------
# sort_transaction_list — dict path (previously untested)
# ---------------------------------------------------------------------------

@pytest.mark.service
def test_sort_pending_after_cleared_dicts():
    """Dict branch: pending sorts after cleared."""
    cleared = _make_dict(1, "cleared", TODAY, -10)
    pending = _make_dict(2, "pending", TODAY, -10)

    result = sort_transaction_list([pending, cleared])
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2


@pytest.mark.service
def test_sort_by_date_ascending_dicts():
    """Dict branch: earlier date sorts first."""
    t1 = _make_dict(1, "pending", TOMORROW, -10)
    t2 = _make_dict(2, "pending", TODAY, -10)

    result = sort_transaction_list([t1, t2])
    assert result[0]["transaction_date"] == TODAY


@pytest.mark.service
def test_sort_mixed_priority_multiple_transactions_dicts():
    """Dict branch: cleared < default < pending, secondary by date."""
    t_pending_late = _make_dict(1, "pending", TOMORROW, -10)
    t_pending_early = _make_dict(2, "pending", TODAY, -10)
    t_cleared = _make_dict(3, "cleared", TOMORROW, -10)

    result = sort_transaction_list([t_pending_late, t_pending_early, t_cleared])
    assert result[0]["id"] == 3   # cleared first regardless of date
    assert result[1]["id"] == 2   # pending today before pending tomorrow
    assert result[2]["id"] == 1


# ---------------------------------------------------------------------------
# add_balances_to_transaction_list — object path
# ---------------------------------------------------------------------------

@pytest.mark.service
def test_add_balances_object_path():
    """Balances accumulate sequentially from start_balance (object path)."""
    t1 = _make_stub(1, "cleared", TODAY, -10)
    t2 = _make_stub(2, "cleared", TODAY, -25)

    result = add_balances_to_transaction_list([t1, t2], start_balance=Decimal("100"))

    assert result[0].balance == Decimal("90")   # 100 + (-10)
    assert result[1].balance == Decimal("65")   # 90 + (-25)


@pytest.mark.service
def test_add_balances_income_increases_balance_objects():
    """Positive pretty_total increases balance."""
    t = _make_stub(1, "cleared", TODAY, 50)

    result = add_balances_to_transaction_list([t], start_balance=Decimal("100"))
    assert result[0].balance == Decimal("150")


# ---------------------------------------------------------------------------
# add_balances_to_transaction_list — dict path (previously untested)
# ---------------------------------------------------------------------------

@pytest.mark.service
def test_add_balances_dict_path():
    """Balances accumulate sequentially from start_balance (dict path)."""
    t1 = _make_dict(1, "cleared", TODAY, -10)
    t2 = _make_dict(2, "cleared", TODAY, -25)

    result = add_balances_to_transaction_list([t1, t2], start_balance=Decimal("100"))

    assert result[0]["balance"] == Decimal("90")
    assert result[1]["balance"] == Decimal("65")


@pytest.mark.service
def test_add_balances_income_increases_balance_dicts():
    """Dict path: positive pretty_total increases balance."""
    t = _make_dict(1, "cleared", TODAY, 50)
    result = add_balances_to_transaction_list([t], start_balance=Decimal("100"))
    assert result[0]["balance"] == Decimal("150")


@pytest.mark.service
def test_add_balances_zero_start_balance_dicts():
    """Dict path: zero start balance works correctly."""
    t1 = _make_dict(1, "cleared", TODAY, -30)
    t2 = _make_dict(2, "cleared", TODAY, 10)

    result = add_balances_to_transaction_list([t1, t2], start_balance=Decimal("0"))
    assert result[0]["balance"] == Decimal("-30")
    assert result[1]["balance"] == Decimal("-20")


# ---------------------------------------------------------------------------
# annotate_transaction_total — DB-level pretty_total sign logic
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_expense_produces_negative_pretty_total(
    test_checking_account, test_pending_transaction_status, test_expense_transaction_type
):
    """Expense transactions produce a negative pretty_total."""
    t = Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("50.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )

    qs = annotate_transaction_total(Transaction.objects.filter(id=t.id), test_checking_account.id)
    assert qs.get().pretty_total == Decimal("-50.00")


@pytest.mark.django_db
@pytest.mark.service
def test_transfer_is_negative_from_source_perspective(
    test_checking_account,
    test_savings_account,
    test_pending_transaction_status,
):
    from transactions.models import TransactionType
    transfer_type, _ = TransactionType.objects.get_or_create(transaction_type='Transfer')

    t = Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("100.00"),
        status=test_pending_transaction_status,
        transaction_type=transfer_type,
        source_account=test_checking_account,
        destination_account=test_savings_account,
    )

    qs = annotate_transaction_total(Transaction.objects.filter(id=t.id), test_checking_account.id)
    assert qs.get().pretty_total == Decimal("-100.00")


@pytest.mark.django_db
@pytest.mark.service
def test_transfer_is_positive_from_destination_perspective(
    test_checking_account,
    test_savings_account,
    test_pending_transaction_status,
):
    from transactions.models import TransactionType
    transfer_type, _ = TransactionType.objects.get_or_create(transaction_type='Transfer')

    t = Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("100.00"),
        status=test_pending_transaction_status,
        transaction_type=transfer_type,
        source_account=test_checking_account,
        destination_account=test_savings_account,
    )

    qs = annotate_transaction_total(Transaction.objects.filter(id=t.id), test_savings_account.id)
    assert qs.get().pretty_total == Decimal("100.00")


# ---------------------------------------------------------------------------
# get_transactions_by_account — combined list ordering
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_cleared_transactions_appear_before_pending(
    test_checking_account,
    test_pending_transaction_status,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """Cleared transactions always appear before pending in the combined list."""
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("10.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Pending",
    )
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("10.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Cleared",
    )

    transactions, _ = get_transactions_by_account(
        end_date=NEXT_WEEK,
        account_id=test_checking_account.id,
        totals_only=False,
    )

    descriptions = [t.description for t in transactions]
    assert descriptions.index("Cleared") < descriptions.index("Pending")


@pytest.mark.django_db
@pytest.mark.service
def test_forecast_transactions_included_as_simulated(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """Forecast cache transactions appear in the list with simulated=True and id < -10000."""
    ForecastCacheTransaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("75.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Estimated Payment",
    )

    transactions, _ = get_transactions_by_account(
        end_date=NEXT_WEEK,
        account_id=test_checking_account.id,
        totals_only=False,
    )

    simulated = [t for t in transactions if t.simulated]
    assert len(simulated) >= 1
    forecast_ids = [t.id for t in simulated if t.id < -10000]
    assert len(forecast_ids) >= 1


@pytest.mark.django_db
@pytest.mark.service
def test_reminder_transactions_included_as_simulated(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
    test_reminder,
):
    """Reminder cache transactions appear in the list with simulated=True and negative id."""
    ReminderCacheTransaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("50.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Scheduled Bill",
        reminder=test_reminder,
    )

    transactions, _ = get_transactions_by_account(
        end_date=NEXT_WEEK,
        account_id=test_checking_account.id,
        totals_only=False,
    )

    reminder_entries = [t for t in transactions if t.simulated and t.id > -10000]
    assert len(reminder_entries) >= 1


@pytest.mark.django_db
@pytest.mark.service
def test_balance_threads_correctly_through_combined_list(
    test_checking_account,
    test_pending_transaction_status,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """Each transaction's balance equals the previous balance plus its pretty_total."""
    # opening=55.55, archive=555.55 → base = 611.10
    Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("100.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Cleared expense",
    )
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("50.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Pending expense",
    )

    transactions, _ = get_transactions_by_account(
        end_date=NEXT_WEEK,
        account_id=test_checking_account.id,
        totals_only=False,
    )

    # Verify each consecutive balance differs by exactly pretty_total
    for i in range(1, len(transactions)):
        prev = transactions[i - 1]
        curr = transactions[i]
        expected = prev.balance + curr.pretty_total
        assert curr.balance == expected, (
            f"Balance mismatch at position {i}: "
            f"prev={prev.balance}, pretty_total={curr.pretty_total}, "
            f"expected={expected}, got={curr.balance}"
        )


# ---------------------------------------------------------------------------
# get_transactions_by_account — forecast path
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_forecast_filters_to_start_date(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """forecast=True only returns transactions on or after start_date."""
    Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("10.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Before start",
    )
    Transaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("20.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="After start",
    )

    transactions, _ = get_transactions_by_account(
        end_date=NEXT_WEEK,
        account_id=test_checking_account.id,
        totals_only=False,
        forecast=True,
        start_date=TODAY,
    )

    descriptions = [t.description for t in transactions]
    assert "Before start" not in descriptions
    assert "After start" in descriptions


@pytest.mark.django_db
@pytest.mark.service
def test_forecast_previous_balance_uses_last_transaction_before_start(
    test_checking_account,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """previous_balance returned by forecast path equals balance of last transaction before start_date."""
    # opening=55.55, archive=555.55 → base = 611.10
    Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("100.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Pre-start cleared",
    )

    _, previous_balance = get_transactions_by_account(
        end_date=NEXT_WEEK,
        account_id=test_checking_account.id,
        totals_only=False,
        forecast=True,
        start_date=TODAY,
    )

    # base 611.10 − 100.00 = 511.10
    assert previous_balance == Decimal("511.10")


@pytest.mark.django_db
@pytest.mark.service
def test_forecast_previous_balance_falls_back_to_opening_when_no_prior_transactions(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """When no transactions exist before start_date, previous_balance = opening + archive."""
    Transaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("20.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Future only",
    )

    _, previous_balance = get_transactions_by_account(
        end_date=NEXT_WEEK,
        account_id=test_checking_account.id,
        totals_only=False,
        forecast=True,
        start_date=TODAY,
    )

    # opening=55.55 + archive=555.55 = 611.10
    assert previous_balance == Decimal("611.10")


@pytest.mark.django_db
@pytest.mark.service
def test_forecast_includes_forecast_cache_transactions(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """Forecast cache transactions appear in the forecast-mode transaction list."""
    ForecastCacheTransaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("150.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Forecast Payment",
    )

    transactions, _ = get_transactions_by_account(
        end_date=NEXT_WEEK,
        account_id=test_checking_account.id,
        totals_only=False,
        forecast=True,
        start_date=TODAY,
    )

    descriptions = [t.description for t in transactions]
    assert "Forecast Payment" in descriptions


@pytest.mark.django_db
@pytest.mark.service
def test_forecast_balance_threads_correctly_from_previous_balance(
    test_checking_account,
    test_cleared_transaction_status,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """In forecast mode, each transaction's balance accumulates from previous_balance."""
    # Cleared transaction before start — establishes previous_balance
    Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("100.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )
    # Future transactions that should appear in forecast
    ForecastCacheTransaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("50.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Forecast A",
    )
    ForecastCacheTransaction.objects.create(
        transaction_date=NEXT_WEEK,
        total_amount=Decimal("25.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Forecast B",
    )

    transactions, previous_balance = get_transactions_by_account(
        end_date=NEXT_WEEK + timedelta(days=1),
        account_id=test_checking_account.id,
        totals_only=False,
        forecast=True,
        start_date=TODAY,
    )

    # previous_balance = 611.10 − 100.00 = 511.10
    assert previous_balance == Decimal("511.10")

    # Each transaction balance must equal previous + cumulative pretty_total
    running = previous_balance
    for t in transactions:
        running += t.pretty_total
        assert t.balance == running, (
            f"{t.description}: expected balance {running}, got {t.balance}"
        )


# ---------------------------------------------------------------------------
# API-level: list endpoint with forecast=true
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_forecast_list_endpoint_returns_200(api_client, test_checking_account):
    response = api_client.get(
        f"/transactions/list?forecast=true&account={test_checking_account.id}&maxdays=30&view_type=1",
        headers=AUTH,
    )
    assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.api
def test_forecast_list_endpoint_includes_forecast_transactions(
    api_client,
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """The list endpoint with forecast=true returns forecast cache transactions."""
    ForecastCacheTransaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("99.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="API Forecast Test",
    )

    response = api_client.get(
        f"/transactions/list?forecast=true&account={test_checking_account.id}&maxdays=30&view_type=1",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    descriptions = [t["description"] for t in data["transactions"]]
    assert "API Forecast Test" in descriptions


@pytest.mark.django_db
@pytest.mark.api
def test_forecast_list_excludes_past_transactions(
    api_client,
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """The forecast list endpoint does not return transactions before today."""
    Transaction.objects.create(
        transaction_date=date(2020, 1, 1),
        total_amount=Decimal("10.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Old transaction",
    )

    response = api_client.get(
        f"/transactions/list?forecast=true&account={test_checking_account.id}&maxdays=30&view_type=1",
        headers=AUTH,
    )

    assert response.status_code == 200
    descriptions = [t["description"] for t in response.json()["transactions"]]
    assert "Old transaction" not in descriptions
