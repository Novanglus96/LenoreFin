"""
CC interest and payment forecast tests.

Covers:
  - calculate_interest — pure formula tests (unit, no DB)
  - generate_statement_cycles — cycle date generation and transaction aggregation
  - update_cc_forecast_cache — full integration: early-return guards, all three payment
    strategies, existing-payment deduplication, zero-balance guard, cache management,
    last_statement_amount update

Note on interest in update_cc_forecast_cache:
  The interest condition is `statement_cycles[0]["statement_due"] < today`.
  Because statement_due is incremented twice (once before the loop, once inside it),
  it always lands ~2 months in the future — making this branch unreachable in normal
  operation.  calculate_interest is therefore tested in isolation below, and the
  update_cc_forecast_cache tests focus on the payment path.
"""
import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import patch

from transactions.tasks import calculate_interest, generate_statement_cycles, update_cc_forecast_cache
from transactions.models import Transaction, ForecastCacheTransaction, TransactionStatus, TransactionType
from transactions.api.dependencies.transaction_utilities import annotate_transaction_total

# Fixed date used across all tests that need a predictable today.
# statement_day=1, today.day=15 → today.day > statement_day → statement_start = 2026-06-01
FIXED_TODAY = date(2026, 6, 15)
PATCH_TODAY = "transactions.tasks.get_todays_date_timezone_adjusted"

AUTH = {"Authorization": "Bearer test-api-key"}


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


def _seed_required_models():
    """Seed the objects that update_cc_forecast_cache needs to function correctly.

    create_transactions.py uses hardcoded type IDs 1=expense, 2=income, 3=transfer.
    SQLite rolls back ROWID on savepoint, so IDs are deterministic: we must create
    expense before income before transfer to guarantee they land on IDs 1, 2, 3.

    Tags 9 (Credit Card) and 18 (Interest Charged) are hardcoded in
    update_cc_forecast_cache and stored as FKs in ForecastCacheTransactionDetail.
    They must exist to avoid FK constraint errors during test teardown.
    """
    _pending_status()
    _expense_type()   # → ID 1
    _income_type()    # → ID 2
    _transfer_type()  # → ID 3
    # Seed the specific Tag IDs embedded in update_cc_forecast_cache
    from tags.models import Tag, TagType, MainTag, SubTag
    tag_type, _ = TagType.objects.get_or_create(tag_type="SystemTest")
    main_tag, _ = MainTag.objects.get_or_create(
        tag_name="SystemTest", defaults={"tag_type": tag_type}
    )
    # (parent_id, child_id) is unique on Tag — use distinct subtags for each seed tag
    sub_cc, _ = SubTag.objects.get_or_create(
        tag_name="CreditCardSeed", defaults={"tag_type": tag_type}
    )
    sub_interest, _ = SubTag.objects.get_or_create(
        tag_name="InterestSeed", defaults={"tag_type": tag_type}
    )
    Tag.objects.get_or_create(
        id=9, defaults={"parent": main_tag, "child": sub_cc, "tag_type": tag_type}
    )
    Tag.objects.get_or_create(
        id=18, defaults={"parent": main_tag, "child": sub_interest, "tag_type": tag_type}
    )


def _make_cc_account(bank, credit_card_account_type, checking_account,
                     strategy="F", payment_amount=None, min_payment=None,
                     opening_balance=Decimal("0.00"), annual_rate=Decimal("18.00"),
                     calculate_payments=True, calculate_interest=False):
    """Create a CC account wired for payment calculations.
    Also seeds the TransactionStatus/TransactionType objects that
    update_cc_forecast_cache looks up by slug inside its try/except block."""
    _seed_required_models()
    from accounts.models import Account
    return Account.objects.create(
        account_name="Test CC",
        account_type=credit_card_account_type,
        opening_balance=opening_balance,
        archive_balance=Decimal("0.00"),
        annual_rate=annual_rate,
        active=True,
        open_date=FIXED_TODAY,
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=10000,
        bank=bank,
        last_statement_amount=Decimal("0.00"),
        funding_account=checking_account,
        calculate_payments=calculate_payments,
        calculate_interest=calculate_interest,
        payment_strategy=strategy,
        payment_amount=payment_amount or Decimal("50.00"),
        minimum_payment_amount=min_payment or Decimal("25.00"),
        statement_day=1,
        due_day=25,
        pay_day=25,
    )


def _expense_type():
    t, _ = TransactionType.objects.get_or_create(transaction_type="Expense")
    return t


def _transfer_type():
    t, _ = TransactionType.objects.get_or_create(transaction_type="Transfer")
    return t


def _pending_status():
    s, _ = TransactionStatus.objects.get_or_create(transaction_status="Pending")
    return s


# ---------------------------------------------------------------------------
# calculate_interest — pure unit tests (no DB)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_basic_interest_calculation():
    """18% APR on $1000 for 30 days = $1000 * (18/365/100) * 30 ≈ $14.79."""
    result = calculate_interest(
        amount=Decimal("-1000.00"),
        annual_rate=Decimal("18.00"),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )
    expected = (Decimal("-1000.00") * (Decimal("18.00") / 365 / 100) * 30).quantize(Decimal("0.01"))
    assert result == expected


@pytest.mark.unit
def test_interest_zero_amount():
    """Zero balance produces zero interest."""
    result = calculate_interest(
        amount=Decimal("0.00"),
        annual_rate=Decimal("18.00"),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 2, 1),
    )
    assert result == Decimal("0.00")


@pytest.mark.unit
def test_interest_zero_days():
    """Same start and end date produces zero interest."""
    result = calculate_interest(
        amount=Decimal("-500.00"),
        annual_rate=Decimal("18.00"),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 1),
    )
    assert result == Decimal("0.00")


@pytest.mark.unit
def test_interest_negative_amount_gives_negative_interest():
    """Negative amount (unpaid CC balance) produces negative interest (additional charge)."""
    result = calculate_interest(
        amount=Decimal("-200.00"),
        annual_rate=Decimal("12.00"),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 2, 1),
    )
    assert result < Decimal("0.00")


@pytest.mark.unit
def test_interest_rounds_half_up():
    """Result is rounded to 2 decimal places using ROUND_HALF_UP."""
    result = calculate_interest(
        amount=Decimal("-100.00"),
        annual_rate=Decimal("5.00"),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 2),
    )
    # $100 * (5/365/100) * 1 = 0.013698..., rounds to 0.01
    assert result == Decimal("-0.01")


@pytest.mark.unit
def test_interest_proportional_to_days():
    """Interest over 60 days is exactly double interest over 30 days."""
    base = calculate_interest(
        amount=Decimal("-1000.00"),
        annual_rate=Decimal("18.00"),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
    )
    double = calculate_interest(
        amount=Decimal("-1000.00"),
        annual_rate=Decimal("18.00"),
        start_date=date(2026, 1, 1),
        end_date=date(2026, 3, 2),  # 60 days
    )
    # Allow 1 cent difference due to rounding
    assert abs(double - (base * 2)) <= Decimal("0.01")


# ---------------------------------------------------------------------------
# generate_statement_cycles — cycle date and aggregation tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_cycles_generated_up_to_forecast_end_date(
    bank, credit_card_account_type, test_checking_account,
):
    """generate_statement_cycles produces roughly 12 monthly cycles for a 1-year window."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(bank, credit_card_account_type, test_checking_account)
        transactions_qs = annotate_transaction_total(
            Transaction.objects.filter(source_account_id=cc.id), cc.id
        )
        from transactions.models import ReminderCacheTransaction
        reminder_qs = annotate_transaction_total(
            ReminderCacheTransaction.objects.filter(source_account_id=cc.id), cc.id
        )
        end_date = FIXED_TODAY + timedelta(days=365)
        cycles, _ = generate_statement_cycles(
            statement_day=1,
            due_day=25,
            pay_day=25,
            forecast_end_date=end_date,
            statement_cycle_length=1,
            statement_cycle_period="m",
            transactions=transactions_qs,
            reminder_transactions=reminder_qs,
            account_id=cc.id,
            non_trans_bal=Decimal("0.00"),
        )
    assert len(cycles) >= 12


@pytest.mark.django_db
@pytest.mark.service
def test_first_cycle_start_when_today_after_statement_day(
    bank, credit_card_account_type, test_checking_account,
):
    """When today.day > statement_day, first cycle starts on statement_day this month."""
    # FIXED_TODAY = 2026-06-15, statement_day=1, so today.day(15) > 1
    # → statement_start = 2026-06-01
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(bank, credit_card_account_type, test_checking_account)
        transactions_qs = annotate_transaction_total(
            Transaction.objects.filter(source_account_id=cc.id), cc.id
        )
        from transactions.models import ReminderCacheTransaction
        reminder_qs = annotate_transaction_total(
            ReminderCacheTransaction.objects.filter(source_account_id=cc.id), cc.id
        )
        cycles, _ = generate_statement_cycles(
            statement_day=1,
            due_day=25,
            pay_day=25,
            forecast_end_date=FIXED_TODAY + timedelta(days=60),
            statement_cycle_length=1,
            statement_cycle_period="m",
            transactions=transactions_qs,
            reminder_transactions=reminder_qs,
            account_id=cc.id,
            non_trans_bal=Decimal("0.00"),
        )
    assert cycles[0]["statement_start"] == date(2026, 6, 1)
    assert cycles[0]["statement_end"] == date(2026, 7, 1)


@pytest.mark.django_db
@pytest.mark.service
def test_first_cycle_start_when_today_before_statement_day(
    bank, credit_card_account_type, test_checking_account,
):
    """When today.day <= statement_day, first cycle starts on statement_day last month."""
    # today=2026-06-05, statement_day=15 → today.day(5) < 15
    # → statement_start = 2026-05-15
    today = date(2026, 6, 5)
    with patch(PATCH_TODAY, return_value=today):
        cc = _make_cc_account(bank, credit_card_account_type, test_checking_account)
        transactions_qs = annotate_transaction_total(
            Transaction.objects.filter(source_account_id=cc.id), cc.id
        )
        from transactions.models import ReminderCacheTransaction
        reminder_qs = annotate_transaction_total(
            ReminderCacheTransaction.objects.filter(source_account_id=cc.id), cc.id
        )
        cycles, _ = generate_statement_cycles(
            statement_day=15,
            due_day=25,
            pay_day=25,
            forecast_end_date=today + timedelta(days=60),
            statement_cycle_length=1,
            statement_cycle_period="m",
            transactions=transactions_qs,
            reminder_transactions=reminder_qs,
            account_id=cc.id,
            non_trans_bal=Decimal("0.00"),
        )
    assert cycles[0]["statement_start"] == date(2026, 5, 15)
    assert cycles[0]["statement_end"] == date(2026, 6, 15)


@pytest.mark.django_db
@pytest.mark.service
def test_cycle_debits_only_include_transactions_in_period(
    bank, credit_card_account_type, test_checking_account,
):
    """Only expenses with transaction_date > statement_start and <= statement_end count."""
    # statement_start=2026-06-01, statement_end=2026-07-01
    # Expense on 2026-06-15 (in period) → counted
    # Expense on 2026-05-31 (before period) → not counted
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(bank, credit_card_account_type, test_checking_account)
        Transaction.objects.create(
            transaction_date=date(2026, 6, 15),
            total_amount=Decimal("100.00"),
            status=_pending_status(),
            transaction_type=_expense_type(),
            source_account=cc,
        )
        Transaction.objects.create(
            transaction_date=date(2026, 5, 31),
            total_amount=Decimal("50.00"),
            status=_pending_status(),
            transaction_type=_expense_type(),
            source_account=cc,
        )

        transactions_qs = annotate_transaction_total(
            Transaction.objects.filter(source_account_id=cc.id), cc.id
        )
        from transactions.models import ReminderCacheTransaction
        reminder_qs = annotate_transaction_total(
            ReminderCacheTransaction.objects.filter(source_account_id=cc.id), cc.id
        )
        cycles, _ = generate_statement_cycles(
            statement_day=1,
            due_day=25,
            pay_day=25,
            forecast_end_date=FIXED_TODAY + timedelta(days=60),
            statement_cycle_length=1,
            statement_cycle_period="m",
            transactions=transactions_qs,
            reminder_transactions=reminder_qs,
            account_id=cc.id,
            non_trans_bal=Decimal("0.00"),
        )

    # Cycle 0: 2026-06-01 to 2026-07-01 — only the June 15 expense ($100) is in it
    assert cycles[0]["statement_debits"] == Decimal("-100.00")


@pytest.mark.django_db
@pytest.mark.service
def test_previous_balance_includes_non_trans_bal_and_prior_transactions(
    bank, credit_card_account_type, test_checking_account,
):
    """previous_balance = non_trans_bal + sum of transactions on or before statement_start."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(bank, credit_card_account_type, test_checking_account)
        # Expense on 2026-05-31 — before statement_start (2026-06-01), so included in previous_balance
        Transaction.objects.create(
            transaction_date=date(2026, 5, 31),
            total_amount=Decimal("75.00"),
            status=_pending_status(),
            transaction_type=_expense_type(),
            source_account=cc,
        )

        transactions_qs = annotate_transaction_total(
            Transaction.objects.filter(source_account_id=cc.id), cc.id
        )
        from transactions.models import ReminderCacheTransaction
        reminder_qs = annotate_transaction_total(
            ReminderCacheTransaction.objects.filter(source_account_id=cc.id), cc.id
        )
        non_trans_bal = Decimal("-50.00")
        cycles, _ = generate_statement_cycles(
            statement_day=1,
            due_day=25,
            pay_day=25,
            forecast_end_date=FIXED_TODAY + timedelta(days=60),
            statement_cycle_length=1,
            statement_cycle_period="m",
            transactions=transactions_qs,
            reminder_transactions=reminder_qs,
            account_id=cc.id,
            non_trans_bal=non_trans_bal,
        )

    # previous_balance = -50.00 + (-75.00) = -125.00
    assert cycles[0]["previous_balance"] == Decimal("-125.00")


# ---------------------------------------------------------------------------
# update_cc_forecast_cache — integration tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
def test_non_cc_account_creates_no_forecast(test_checking_account):
    """update_cc_forecast_cache is a no-op for non-CC accounts."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        update_cc_forecast_cache(test_checking_account.id)

    assert ForecastCacheTransaction.objects.filter(
        source_account_id=test_checking_account.id
    ).count() == 0


@pytest.mark.django_db
@pytest.mark.service
def test_calculate_payments_false_clears_forecast_then_returns(
    bank, credit_card_account_type, test_checking_account,
):
    """When calculate_payments=False, existing ForecastCacheTransaction records are deleted but none created."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(bank, credit_card_account_type, test_checking_account,
                              calculate_payments=False)
        # Pre-populate a forecast record to confirm it gets cleared
        ForecastCacheTransaction.objects.create(
            transaction_date=FIXED_TODAY,
            total_amount=Decimal("100.00"),
            status=_pending_status(),
            transaction_type=_transfer_type(),
            source_account=test_checking_account,
            destination_account=cc,
        )

        update_cc_forecast_cache(cc.id)

    assert ForecastCacheTransaction.objects.filter(
        destination_account_id=cc.id
    ).count() == 0


@pytest.mark.django_db
@pytest.mark.service
def test_full_payment_strategy_creates_payment_equal_to_balance(
    bank, credit_card_account_type, test_checking_account,
):
    """Full strategy: forecast payment = abs(cycle_balance)."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        # opening_balance=-200 → non_trans_bal=-200, no other transactions
        # → cycle_balance = -200 → full payment = $200
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="F", opening_balance=Decimal("-200.00"),
        )
        update_cc_forecast_cache(cc.id)

    payments = ForecastCacheTransaction.objects.filter(
        source_account_id=test_checking_account.id,
        destination_account_id=cc.id,
    )
    assert payments.count() >= 1
    assert payments.first().total_amount == Decimal("-200.00")


@pytest.mark.django_db
@pytest.mark.service
def test_minimum_payment_strategy_pays_minimum_when_balance_exceeds_minimum(
    bank, credit_card_account_type, test_checking_account,
):
    """Minimum strategy: when balance > minimum, forecast = minimum_payment_amount."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="M",
            opening_balance=Decimal("-500.00"),
            min_payment=Decimal("25.00"),
        )
        update_cc_forecast_cache(cc.id)

    payments = ForecastCacheTransaction.objects.filter(
        source_account_id=test_checking_account.id,
        destination_account_id=cc.id,
    )
    assert payments.count() >= 1
    assert payments.first().total_amount == Decimal("-25.00")


@pytest.mark.django_db
@pytest.mark.service
def test_minimum_payment_strategy_pays_full_when_balance_below_minimum(
    bank, credit_card_account_type, test_checking_account,
):
    """Minimum strategy: when balance < minimum, forecast = abs(balance)."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        # balance = -10, minimum = 25 → pays full $10
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="M",
            opening_balance=Decimal("-10.00"),
            min_payment=Decimal("25.00"),
        )
        update_cc_forecast_cache(cc.id)

    payments = ForecastCacheTransaction.objects.filter(
        source_account_id=test_checking_account.id,
        destination_account_id=cc.id,
    )
    assert payments.count() >= 1
    assert payments.first().total_amount == Decimal("-10.00")


@pytest.mark.django_db
@pytest.mark.service
def test_custom_payment_strategy_pays_custom_amount(
    bank, credit_card_account_type, test_checking_account,
):
    """Custom strategy: when balance > payment_amount, forecast = payment_amount."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="C",
            opening_balance=Decimal("-300.00"),
            payment_amount=Decimal("75.00"),
        )
        update_cc_forecast_cache(cc.id)

    payments = ForecastCacheTransaction.objects.filter(
        source_account_id=test_checking_account.id,
        destination_account_id=cc.id,
    )
    assert payments.count() >= 1
    assert payments.first().total_amount == Decimal("-75.00")


@pytest.mark.django_db
@pytest.mark.service
def test_no_payment_when_balance_is_zero(
    bank, credit_card_account_type, test_checking_account,
):
    """No forecast payment when there is no outstanding balance."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="F", opening_balance=Decimal("0.00"),
        )
        update_cc_forecast_cache(cc.id)

    assert ForecastCacheTransaction.objects.filter(
        source_account_id=test_checking_account.id,
        destination_account_id=cc.id,
    ).count() == 0


@pytest.mark.django_db
@pytest.mark.service
def test_existing_payment_reduces_forecast_payment(
    bank, credit_card_account_type, test_checking_account,
):
    """When a transfer payment already exists in the payment window, forecast is reduced by that amount."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="F", opening_balance=Decimal("-200.00"),
        )
        transfer_type = _transfer_type()
        # Existing payment: $100 from checking → CC, dated in the first pay window
        # Payment window: statement_end (2026-07-01) < date <= next_statement_end (2026-08-01)
        Transaction.objects.create(
            transaction_date=date(2026, 7, 15),
            total_amount=Decimal("100.00"),
            status=_pending_status(),
            transaction_type=transfer_type,
            source_account=test_checking_account,
            destination_account=cc,
        )
        update_cc_forecast_cache(cc.id)

    payments = ForecastCacheTransaction.objects.filter(
        source_account_id=test_checking_account.id,
        destination_account_id=cc.id,
    )
    # Full payment would be $200; existing $100 reduces to $100 forecast
    assert payments.count() >= 1
    assert payments.first().total_amount == Decimal("-100.00")


@pytest.mark.django_db
@pytest.mark.service
def test_fully_covered_payment_creates_no_forecast(
    bank, credit_card_account_type, test_checking_account,
):
    """When existing payments fully cover the calculated payment, no forecast is created."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="F", opening_balance=Decimal("-200.00"),
        )
        transfer_type = _transfer_type()
        Transaction.objects.create(
            transaction_date=date(2026, 7, 15),
            total_amount=Decimal("200.00"),
            status=_pending_status(),
            transaction_type=transfer_type,
            source_account=test_checking_account,
            destination_account=cc,
        )
        update_cc_forecast_cache(cc.id)

    assert ForecastCacheTransaction.objects.filter(
        source_account_id=test_checking_account.id,
        destination_account_id=cc.id,
    ).count() == 0


@pytest.mark.django_db
@pytest.mark.service
def test_payment_source_is_funding_account(
    bank, credit_card_account_type, test_checking_account,
):
    """Forecast payment transfer originates from the CC account's funding_account."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="F", opening_balance=Decimal("-100.00"),
        )
        update_cc_forecast_cache(cc.id)

    payments = ForecastCacheTransaction.objects.filter(
        destination_account_id=cc.id,
    )
    assert payments.count() >= 1
    assert payments.first().source_account_id == test_checking_account.id


@pytest.mark.django_db
@pytest.mark.service
def test_last_statement_amount_updated_after_calculation(
    bank, credit_card_account_type, test_checking_account,
):
    """account.last_statement_amount is set to the first cycle's payment after running."""

    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="F", opening_balance=Decimal("-150.00"),
        )
        update_cc_forecast_cache(cc.id)

    cc.refresh_from_db()
    assert cc.last_statement_amount == Decimal("150.00")


@pytest.mark.django_db
@pytest.mark.service
def test_existing_forecast_cleared_before_recalculation(
    bank, credit_card_account_type, test_checking_account,
):
    """Stale ForecastCacheTransaction records are deleted before new ones are created."""
    with patch(PATCH_TODAY, return_value=FIXED_TODAY):
        cc = _make_cc_account(
            bank, credit_card_account_type, test_checking_account,
            strategy="F", opening_balance=Decimal("-100.00"),
        )
        # Run once to create a forecast
        update_cc_forecast_cache(cc.id)
        count_first = ForecastCacheTransaction.objects.filter(
            destination_account_id=cc.id
        ).count()

        # Run again — old forecast cleared and new one created
        update_cc_forecast_cache(cc.id)
        count_second = ForecastCacheTransaction.objects.filter(
            destination_account_id=cc.id
        ).count()

    # Both runs should produce the same count (not accumulate)
    assert count_first == count_second
    assert count_first >= 1
