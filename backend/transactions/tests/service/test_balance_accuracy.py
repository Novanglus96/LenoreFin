"""
Balance accuracy tests.

These tests assert that account balances are always numerically correct —
both for cleared transactions (DB Window function path via annotate_transaction_balance)
and for the full combined list produced by get_transactions_by_account.

Invariants under test:
  1. cleared_balance = opening + archive when no cleared transactions exist
  2. cleared_balance = balance of the last cleared transaction after sort
  3. Each cleared transaction's balance = (opening + archive) + cumulative pretty_total
  4. Pending balances start from cleared_balance and thread forward
  5. Transfers are negative from the source account and positive from the destination
  6. Archived transactions are excluded from the list; only archive_balance represents them
  7. Final balance of the last transaction = opening + archive + sum(all pretty_totals)
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal

from transactions.models import Transaction, TransactionStatus, TransactionType
from transactions.api.dependencies.transaction_utilities import (
    annotate_transaction_balance,
    annotate_transaction_total,
    sort_transactions,
)
from transactions.api.dependencies.get_transactions_by_account import (
    get_transactions_by_account,
)

TODAY = date(2026, 6, 1)
YESTERDAY = TODAY - timedelta(days=1)
TWO_DAYS_AGO = TODAY - timedelta(days=2)
TOMORROW = TODAY + timedelta(days=1)
NEXT_WEEK = TODAY + timedelta(days=7)

BASE_BALANCE = Decimal("611.10")  # opening=55.55 + archive=555.55


@pytest.fixture(autouse=True)
def clear_cache():
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _income_type():
    t, _ = TransactionType.objects.get_or_create(transaction_type="Income")
    return t


def _transfer_type():
    t, _ = TransactionType.objects.get_or_create(transaction_type="Transfer")
    return t


def _archived_status():
    s, _ = TransactionStatus.objects.get_or_create(transaction_status="Archived")
    return s


def _reconciled_status():
    s, _ = TransactionStatus.objects.get_or_create(transaction_status="Reconciled")
    return s


def _get_all(account_id, end=NEXT_WEEK):
    transactions, _ = get_transactions_by_account(
        end_date=end,
        account_id=account_id,
        totals_only=False,
    )
    return transactions


def _annotated_cleared_qs(account, qs):
    """Annotate a queryset with pretty_total, custom_order, then balance (cleared path).
    Mirrors the sequence in get_transactions_by_account: annotate_total → sort_transactions
    (which adds custom_order) → annotate_balance (Window uses custom_order)."""
    qs = annotate_transaction_total(qs, account.id)
    qs = sort_transactions(qs, asc=True)
    return annotate_transaction_balance(qs, account.opening_balance, account.archive_balance)


# ---------------------------------------------------------------------------
# annotate_transaction_balance — DB Window function (cleared path)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_single_cleared_expense_balance(
    test_checking_account,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """One cleared expense: balance = opening + archive + pretty_total."""
    t = Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("100.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )

    qs = Transaction.objects.filter(id=t.id)
    row = _annotated_cleared_qs(test_checking_account, qs).get()

    assert row.balance == BASE_BALANCE - Decimal("100.00")


@pytest.mark.django_db
@pytest.mark.service
def test_single_cleared_income_balance(
    test_checking_account,
    test_cleared_transaction_status,
):
    """One cleared income: balance = opening + archive + income_amount."""
    t = Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("200.00"),
        status=test_cleared_transaction_status,
        transaction_type=_income_type(),
        source_account=test_checking_account,
    )

    qs = Transaction.objects.filter(id=t.id)
    row = _annotated_cleared_qs(test_checking_account, qs).get()

    assert row.balance == BASE_BALANCE + Decimal("200.00")


@pytest.mark.django_db
@pytest.mark.service
def test_two_cleared_expenses_thread_correctly(
    test_checking_account,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """Two cleared expenses on different dates: each balance = base + cumulative sum."""
    t1 = Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("50.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="First",
    )
    t2 = Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("30.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Second",
    )

    qs = Transaction.objects.filter(id__in=[t1.id, t2.id])
    rows = {r.description: r for r in _annotated_cleared_qs(test_checking_account, qs)}

    assert rows["First"].balance == BASE_BALANCE - Decimal("50.00")
    assert rows["Second"].balance == BASE_BALANCE - Decimal("50.00") - Decimal("30.00")


@pytest.mark.django_db
@pytest.mark.service
def test_income_then_expense_cleared_balance(
    test_checking_account,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """Income followed by expense: net balance reflects both."""
    t_income = Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("300.00"),
        status=test_cleared_transaction_status,
        transaction_type=_income_type(),
        source_account=test_checking_account,
        description="Income",
    )
    t_expense = Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("75.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Expense",
    )

    qs = Transaction.objects.filter(id__in=[t_income.id, t_expense.id])
    rows = {r.description: r for r in _annotated_cleared_qs(test_checking_account, qs)}

    assert rows["Income"].balance == BASE_BALANCE + Decimal("300.00")
    assert rows["Expense"].balance == BASE_BALANCE + Decimal("300.00") - Decimal("75.00")


# ---------------------------------------------------------------------------
# get_transactions_by_account — cleared_balance fallback
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_no_cleared_transactions_cleared_balance_is_base(test_checking_account):
    """With no transactions at all, the only result is an empty list and cleared_balance = base."""
    transactions = _get_all(test_checking_account.id)
    assert transactions == []


@pytest.mark.django_db
@pytest.mark.service
def test_cleared_balance_equals_last_cleared_transaction(
    test_checking_account,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """cleared_balance is the balance of the last cleared transaction, which pending then builds on."""
    Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("100.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Cleared",
    )
    pending_status, _ = TransactionStatus.objects.get_or_create(transaction_status="Pending")
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("40.00"),
        status=pending_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Pending",
    )

    transactions = _get_all(test_checking_account.id)
    by_desc = {t.description: t for t in transactions}

    cleared_balance = BASE_BALANCE - Decimal("100.00")
    assert by_desc["Cleared"].balance == cleared_balance
    assert by_desc["Pending"].balance == cleared_balance - Decimal("40.00")


# ---------------------------------------------------------------------------
# Pending balances start from cleared_balance
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_pending_balance_threads_from_opening_when_no_cleared(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """With no cleared transactions, pending balance starts from opening + archive."""
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("55.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Pending only",
    )

    transactions = _get_all(test_checking_account.id)
    assert len(transactions) == 1
    assert transactions[0].balance == BASE_BALANCE - Decimal("55.00")


@pytest.mark.django_db
@pytest.mark.service
def test_multiple_pending_balance_threads_sequentially(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """Multiple pending transactions chain balances sequentially from base."""
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("10.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="P1",
    )
    Transaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("20.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="P2",
    )
    Transaction.objects.create(
        transaction_date=NEXT_WEEK,
        total_amount=Decimal("30.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="P3",
    )

    # end_date uses __lt, so must be strictly after NEXT_WEEK to include P3
    transactions = _get_all(test_checking_account.id, end=NEXT_WEEK + timedelta(days=1))
    by_desc = {t.description: t for t in transactions}

    assert by_desc["P1"].balance == BASE_BALANCE - Decimal("10.00")
    assert by_desc["P2"].balance == BASE_BALANCE - Decimal("10.00") - Decimal("20.00")
    assert by_desc["P3"].balance == BASE_BALANCE - Decimal("10.00") - Decimal("20.00") - Decimal("30.00")


# ---------------------------------------------------------------------------
# Transfer balance accuracy
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_transfer_reduces_source_account_balance(
    test_checking_account,
    test_savings_account,
    test_cleared_transaction_status,
):
    """A cleared transfer reduces the source account balance by the transfer amount."""
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("150.00"),
        status=test_cleared_transaction_status,
        transaction_type=_transfer_type(),
        source_account=test_checking_account,
        destination_account=test_savings_account,
    )

    transactions = _get_all(test_checking_account.id)
    assert len(transactions) == 1
    assert transactions[0].balance == BASE_BALANCE - Decimal("150.00")


@pytest.mark.django_db
@pytest.mark.service
def test_transfer_increases_destination_account_balance(
    test_checking_account,
    test_savings_account,
    test_cleared_transaction_status,
):
    """A cleared transfer increases the destination account balance by the transfer amount."""
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("150.00"),
        status=test_cleared_transaction_status,
        transaction_type=_transfer_type(),
        source_account=test_checking_account,
        destination_account=test_savings_account,
    )

    transactions = _get_all(test_savings_account.id)
    assert len(transactions) == 1
    assert transactions[0].balance == BASE_BALANCE + Decimal("150.00")


@pytest.mark.django_db
@pytest.mark.service
def test_transfer_does_not_double_count_on_source(
    test_checking_account,
    test_savings_account,
    test_cleared_transaction_status,
):
    """The transfer appears once in the source account list, not twice."""
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("50.00"),
        status=test_cleared_transaction_status,
        transaction_type=_transfer_type(),
        source_account=test_checking_account,
        destination_account=test_savings_account,
    )

    transactions = _get_all(test_checking_account.id)
    assert len(transactions) == 1


# ---------------------------------------------------------------------------
# Archived transactions — excluded from list but represented by archive_balance
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_archived_transaction_excluded_from_list(
    test_checking_account,
    test_expense_transaction_type,
):
    """Archived transactions do not appear in the transaction list."""
    Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("999.00"),
        status=_archived_status(),
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Archived",
    )

    transactions = _get_all(test_checking_account.id)
    descriptions = [t.description for t in transactions]
    assert "Archived" not in descriptions


@pytest.mark.django_db
@pytest.mark.service
def test_archive_balance_contributes_to_base_balance(
    bank,
    checking_account_type,
    test_cleared_transaction_status,
    test_expense_transaction_type,
):
    """archive_balance is included in the starting balance for cleared transaction annotation."""
    from accounts.models import Account

    account = Account.objects.create(
        account_name="Archive Balance Test Account",
        account_type=checking_account_type,
        opening_balance=Decimal("100.00"),
        archive_balance=Decimal("200.00"),
        active=True,
        open_date=TODAY,
        bank=bank,
    )

    t = Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("50.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=account,
    )

    qs = Transaction.objects.filter(id=t.id)
    row = _annotated_cleared_qs(account, qs).get()

    # balance = opening(100) + archive(200) + pretty_total(-50) = 250
    assert row.balance == Decimal("250.00")


# ---------------------------------------------------------------------------
# Full sequence — final balance invariant
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_final_balance_equals_base_plus_sum_of_all_pretty_totals(
    test_checking_account,
    test_cleared_transaction_status,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """The last transaction's balance = opening + archive + sum(all pretty_totals)."""
    amounts = [Decimal("50.00"), Decimal("25.00"), Decimal("75.00"), Decimal("10.00")]
    statuses = [
        test_cleared_transaction_status,
        test_cleared_transaction_status,
        test_pending_transaction_status,
        test_pending_transaction_status,
    ]
    dates = [TWO_DAYS_AGO, YESTERDAY, TODAY, TOMORROW]

    for amt, status, d in zip(amounts, statuses, dates):
        Transaction.objects.create(
            transaction_date=d,
            total_amount=amt,
            status=status,
            transaction_type=test_expense_transaction_type,
            source_account=test_checking_account,
        )

    transactions = _get_all(test_checking_account.id)
    assert len(transactions) == 4

    expected_final = BASE_BALANCE - sum(amounts)
    assert transactions[-1].balance == expected_final


@pytest.mark.django_db
@pytest.mark.service
def test_consecutive_balance_differences_equal_pretty_totals(
    test_checking_account,
    test_cleared_transaction_status,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """For every adjacent pair in the combined list: balance[i] - balance[i-1] == pretty_total[i]."""
    Transaction.objects.create(
        transaction_date=YESTERDAY,
        total_amount=Decimal("100.00"),
        status=test_cleared_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("200.00"),
        status=test_cleared_transaction_status,
        transaction_type=_income_type(),
        source_account=test_checking_account,
    )
    Transaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("30.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )

    transactions = _get_all(test_checking_account.id)
    assert len(transactions) == 3

    for i in range(1, len(transactions)):
        prev = transactions[i - 1]
        curr = transactions[i]
        assert curr.balance == prev.balance + curr.pretty_total, (
            f"Position {i}: prev.balance={prev.balance}, "
            f"pretty_total={curr.pretty_total}, "
            f"expected={prev.balance + curr.pretty_total}, got={curr.balance}"
        )


@pytest.mark.django_db
@pytest.mark.service
def test_zero_amount_transaction_does_not_change_balance(
    test_checking_account,
    test_pending_transaction_status,
    test_expense_transaction_type,
):
    """A $0 transaction leaves the running balance unchanged."""
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("0.00"),
        status=test_pending_transaction_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
    )

    transactions = _get_all(test_checking_account.id)
    assert len(transactions) == 1
    assert transactions[0].balance == BASE_BALANCE


@pytest.mark.django_db
@pytest.mark.service
def test_reconciled_transaction_included_in_cleared_balance(
    test_checking_account,
    test_expense_transaction_type,
):
    """Reconciled transactions are treated as cleared and included in cleared_balance."""
    Transaction.objects.create(
        transaction_date=TODAY,
        total_amount=Decimal("88.00"),
        status=_reconciled_status(),
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Reconciled",
    )
    pending_status, _ = TransactionStatus.objects.get_or_create(transaction_status="Pending")
    Transaction.objects.create(
        transaction_date=TOMORROW,
        total_amount=Decimal("12.00"),
        status=pending_status,
        transaction_type=test_expense_transaction_type,
        source_account=test_checking_account,
        description="Pending",
    )

    transactions = _get_all(test_checking_account.id)
    by_desc = {t.description: t for t in transactions}

    # Reconciled acts as cleared — its balance anchors the pending start
    assert by_desc["Reconciled"].balance == BASE_BALANCE - Decimal("88.00")
    assert by_desc["Pending"].balance == BASE_BALANCE - Decimal("88.00") - Decimal("12.00")
