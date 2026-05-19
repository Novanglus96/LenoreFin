"""
Execution service tests for the reports app.

All monetary assertions use Decimal to avoid float rounding surprises.
The fixture set creates a controlled set of transactions across known dates
so that every aggregate can be verified by hand.
"""
import pytest
from datetime import date
from decimal import Decimal

from accounts.models import Account, AccountType, Bank
from tags.models import MainTag, SubTag, Tag, TagType
from transactions.models import Transaction, TransactionDetail, TransactionStatus, TransactionType

from reports.services.execution import (
    _resolve_tag_ids,
    _get_tag_label,
    run_report,
)


# ---------------------------------------------------------------------------
# Shared date constants
# ---------------------------------------------------------------------------
JAN_1 = date(2025, 1, 15)
FEB_1 = date(2025, 2, 10)
MAR_1 = date(2025, 3, 5)
# Prior-year equivalents (for COMPARISON tests)
JAN_1_PY = date(2024, 1, 15)
FEB_1_PY = date(2024, 2, 10)

RANGE_2025 = ("CUSTOM", date(2025, 1, 1), date(2025, 12, 31))
RANGE_2024 = ("CUSTOM", date(2024, 1, 1), date(2024, 12, 31))


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tag_type(db):
    return TagType.objects.create(tag_type="Expense")


@pytest.fixture
def main_tag(tag_type):
    return MainTag.objects.create(tag_name="Food", tag_type=tag_type)


@pytest.fixture
def sub_tag(tag_type):
    return SubTag.objects.create(tag_name="Groceries", tag_type=tag_type)


@pytest.fixture
def other_sub_tag(tag_type):
    return SubTag.objects.create(tag_name="Restaurants", tag_type=tag_type)


@pytest.fixture
def tag(main_tag, sub_tag, tag_type):
    return Tag.objects.create(parent=main_tag, child=sub_tag, tag_type=tag_type)


@pytest.fixture
def other_tag(main_tag, other_sub_tag, tag_type):
    return Tag.objects.create(parent=main_tag, child=other_sub_tag, tag_type=tag_type)


@pytest.fixture
def account_type(db):
    return AccountType.objects.create(account_type="Checking", color="#000", icon="mdi-check")


@pytest.fixture
def bank(db):
    return Bank.objects.create(bank_name="Test Bank")


@pytest.fixture
def account(bank, account_type):
    return Account.objects.create(
        account_name="Checking",
        account_type=account_type,
        opening_balance=0,
        annual_rate=0,
        active=True,
        open_date=date(2020, 1, 1),
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=0,
        bank=bank,
        statement_balance=0,
        archive_balance=0,
    )


@pytest.fixture
def other_account(bank, account_type):
    return Account.objects.create(
        account_name="Savings",
        account_type=account_type,
        opening_balance=0,
        annual_rate=0,
        active=True,
        open_date=date(2020, 1, 1),
        statement_cycle_length=1,
        statement_cycle_period="m",
        credit_limit=0,
        bank=bank,
        statement_balance=0,
        archive_balance=0,
    )


@pytest.fixture
def tx_type(db):
    return TransactionType.objects.create(transaction_type="Expense")


@pytest.fixture
def cleared_status(db):
    return TransactionStatus.objects.create(transaction_status="Cleared")


@pytest.fixture
def pending_status(db):
    return TransactionStatus.objects.create(transaction_status="Pending")


@pytest.fixture
def reconciled_status(db):
    return TransactionStatus.objects.create(transaction_status="Reconciled")


@pytest.fixture
def archived_status(db):
    return TransactionStatus.objects.create(transaction_status="Archived")


def _make_tx(account, status, tx_type, tx_date, amount, tag=None):
    tx = Transaction.objects.create(
        source_account=account,
        status=status,
        transaction_type=tx_type,
        transaction_date=tx_date,
        total_amount=amount,
        description=f"tx {tx_date}",
    )
    TransactionDetail.objects.create(
        transaction=tx,
        detail_amt=amount,
        tag=tag,
    )
    return tx


# ---------------------------------------------------------------------------
# Unit-level: tag ID resolution helpers
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.unit
class TestResolveTagIds:
    def test_specific_tag(self, tag):
        ids = _resolve_tag_ids(tag_id=tag.id)
        assert ids == [tag.id]

    def test_sub_tag_rolls_up(self, tag, sub_tag):
        ids = _resolve_tag_ids(sub_tag_id=sub_tag.id)
        assert tag.id in ids
        assert len(ids) == 1

    def test_main_tag_rolls_up_all_children(self, tag, other_tag, main_tag):
        ids = _resolve_tag_ids(main_tag_id=main_tag.id)
        assert tag.id in ids
        assert other_tag.id in ids

    def test_none_returns_empty(self):
        ids = _resolve_tag_ids()
        assert ids == []


@pytest.mark.django_db
@pytest.mark.unit
class TestGetTagLabel:
    def test_tag_label(self, tag):
        label = _get_tag_label(tag_id=tag.id)
        assert "Groceries" in label

    def test_sub_tag_label(self, sub_tag):
        label = _get_tag_label(sub_tag_id=sub_tag.id)
        assert label == "Groceries"

    def test_main_tag_label(self, main_tag):
        label = _get_tag_label(main_tag_id=main_tag.id)
        assert label == "Food"

    def test_missing_tag_id_fallback(self):
        label = _get_tag_label(tag_id=999999)
        assert "999999" in label


# ---------------------------------------------------------------------------
# Service: run_report — TOTALS
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
class TestRunReportTotalsTag:
    def test_empty_selections_returns_all_tags_row(
        self, account, cleared_status, tx_type, tag
    ):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, FEB_1, Decimal("-50.00"), tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        assert result["report_type"] == "TOTALS"
        assert len(result["rows"]) == 1
        assert result["rows"][0]["label"] == "All Tags"
        assert result["rows"][0]["total"] == Decimal("-150.00")
        assert result["subtotal"] == Decimal("-150.00")

    def test_specific_tag_selection(self, account, cleared_status, tx_type, tag, other_tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, FEB_1, Decimal("-80.00"), other_tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[{"tag_id": tag.id, "sub_tag_id": None, "main_tag_id": None}],
            show_transactions=False,
            show_subtotal=False,
            include_pending=False,
        )
        assert len(result["rows"]) == 1
        assert result["rows"][0]["total"] == Decimal("-100.00")
        assert "subtotal" not in result or result.get("subtotal") is None

    def test_main_tag_rolls_up_both_children(
        self, account, cleared_status, tx_type, main_tag, tag, other_tag
    ):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, FEB_1, Decimal("-80.00"), other_tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[{"tag_id": None, "sub_tag_id": None, "main_tag_id": main_tag.id}],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("-180.00")

    def test_sub_tag_rolls_up(self, account, cleared_status, tx_type, sub_tag, tag, other_tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, FEB_1, Decimal("-80.00"), other_tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[{"tag_id": None, "sub_tag_id": sub_tag.id, "main_tag_id": None}],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        # sub_tag maps only to `tag`, not `other_tag`
        assert result["rows"][0]["total"] == Decimal("-100.00")

    def test_multiple_selections_produce_separate_rows(
        self, account, cleared_status, tx_type, tag, other_tag
    ):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, FEB_1, Decimal("-80.00"), other_tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[
                {"tag_id": tag.id, "sub_tag_id": None, "main_tag_id": None},
                {"tag_id": other_tag.id, "sub_tag_id": None, "main_tag_id": None},
            ],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        assert len(result["rows"]) == 2
        totals = {r["label"]: r["total"] for r in result["rows"]}
        groceries_label = next(k for k in totals if "Groceries" in k)
        restaurants_label = next(k for k in totals if "Restaurants" in k)
        assert totals[groceries_label] == Decimal("-100.00")
        assert totals[restaurants_label] == Decimal("-80.00")
        assert result["subtotal"] == Decimal("-180.00")

    def test_empty_date_range_returns_zero(self, account, cleared_status, tx_type, tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("0.00")

    def test_show_subtotal_false_omits_subtotal(self, account, cleared_status, tx_type, tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=False,
            include_pending=False,
        )
        assert result.get("subtotal") is None

    def test_show_transactions_true(self, account, cleared_status, tx_type, tag):
        tx = _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-50.00"), tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=True,
            show_subtotal=False,
            include_pending=False,
        )
        txs = result["rows"][0]["transactions"]
        assert len(txs) == 1
        assert txs[0]["id"] == tx.id
        assert txs[0]["amount"] == Decimal("-50.00")

    def test_show_transactions_false_omits_key(self, account, cleared_status, tx_type, tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-50.00"), tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=False,
            include_pending=False,
        )
        assert result["rows"][0].get("transactions") is None


@pytest.mark.django_db
@pytest.mark.service
class TestRunReportTotalsMonth:
    def test_month_labels_and_counts(self, account, cleared_status, tx_type, tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, MAR_1, Decimal("-60.00"), tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="MONTH",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 3, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        assert result["group_by"] == "MONTH"
        assert len(result["rows"]) == 3
        labels = [r["label"] for r in result["rows"]]
        assert "January 2025" in labels
        assert "February 2025" in labels
        assert "March 2025" in labels

    def test_month_totals_correct(self, account, cleared_status, tx_type, tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, FEB_1, Decimal("-200.00"), tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="MONTH",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 2, 28),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        by_month = {r["label"]: r["total"] for r in result["rows"]}
        assert by_month["January 2025"] == Decimal("-100.00")
        assert by_month["February 2025"] == Decimal("-200.00")
        assert result["subtotal"] == Decimal("-300.00")

    def test_empty_month_has_zero_total(self, account, cleared_status, tx_type, tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="MONTH",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 2, 28),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=False,
            include_pending=False,
        )
        by_month = {r["label"]: r["total"] for r in result["rows"]}
        assert by_month["February 2025"] == Decimal("0.00")

    def test_month_respects_tag_filter(self, account, cleared_status, tx_type, tag, other_tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-999.00"), other_tag)

        result = run_report(
            report_type="TOTALS",
            date_range_type="CUSTOM",
            group_by="MONTH",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 1, 31),
            account_ids=[],
            tag_selections=[{"tag_id": tag.id, "sub_tag_id": None, "main_tag_id": None}],
            show_transactions=False,
            show_subtotal=False,
            include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("-100.00")


# ---------------------------------------------------------------------------
# Service: run_report — COMPARISON
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
class TestRunReportComparison:
    def test_comparison_shifts_prior_period_one_year(
        self, account, cleared_status, tx_type, tag
    ):
        # 2025 transaction
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        # 2024 transaction (prior year)
        _make_tx(account, cleared_status, tx_type, JAN_1_PY, Decimal("-80.00"), tag)

        result = run_report(
            report_type="COMPARISON",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        assert result["period2_from"] == date(2024, 1, 1)
        assert result["period2_to"] == date(2024, 12, 31)
        assert result["rows"][0]["period1_total"] == Decimal("-100.00")
        assert result["rows"][0]["period2_total"] == Decimal("-80.00")
        assert result["rows"][0]["difference"] == Decimal("-20.00")

    def test_comparison_subtotals(self, account, cleared_status, tx_type, tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, JAN_1_PY, Decimal("-60.00"), tag)

        result = run_report(
            report_type="COMPARISON",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        assert result["subtotal"] == Decimal("-100.00")
        assert result["subtotal2"] == Decimal("-60.00")

    def test_comparison_month_groupby_returns_single_total_row(
        self, account, cleared_status, tx_type, tag
    ):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, FEB_1, Decimal("-50.00"), tag)
        _make_tx(account, cleared_status, tx_type, JAN_1_PY, Decimal("-80.00"), tag)

        result = run_report(
            report_type="COMPARISON",
            date_range_type="CUSTOM",
            group_by="MONTH",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[],
            show_transactions=False,
            show_subtotal=True,
            include_pending=False,
        )
        assert len(result["rows"]) == 1
        assert result["rows"][0]["label"] == "Total"
        assert result["rows"][0]["period1_total"] == Decimal("-150.00")
        assert result["rows"][0]["period2_total"] == Decimal("-80.00")

    def test_comparison_tag_rows(self, account, cleared_status, tx_type, tag, other_tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-200.00"), other_tag)
        _make_tx(account, cleared_status, tx_type, JAN_1_PY, Decimal("-90.00"), tag)
        _make_tx(account, cleared_status, tx_type, JAN_1_PY, Decimal("-180.00"), other_tag)

        result = run_report(
            report_type="COMPARISON",
            date_range_type="CUSTOM",
            group_by="TAG",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            account_ids=[],
            tag_selections=[
                {"tag_id": tag.id, "sub_tag_id": None, "main_tag_id": None},
                {"tag_id": other_tag.id, "sub_tag_id": None, "main_tag_id": None},
            ],
            show_transactions=False,
            show_subtotal=False,
            include_pending=False,
        )
        assert len(result["rows"]) == 2
        by_label = {r["label"]: r for r in result["rows"]}
        groceries_key = next(k for k in by_label if "Groceries" in k)
        restaurants_key = next(k for k in by_label if "Restaurants" in k)
        assert by_label[groceries_key]["period1_total"] == Decimal("-100.00")
        assert by_label[groceries_key]["period2_total"] == Decimal("-90.00")
        assert by_label[restaurants_key]["period1_total"] == Decimal("-200.00")


# ---------------------------------------------------------------------------
# Service: status filtering
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
class TestStatusFiltering:
    def test_cleared_included_by_default(self, account, cleared_status, tx_type, tag):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        result = run_report(
            report_type="TOTALS", date_range_type="CUSTOM", group_by="TAG",
            date_from=date(2025, 1, 1), date_to=date(2025, 12, 31),
            account_ids=[], tag_selections=[], show_transactions=False,
            show_subtotal=False, include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("-100.00")

    def test_reconciled_included_by_default(self, account, reconciled_status, tx_type, tag):
        _make_tx(account, reconciled_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        result = run_report(
            report_type="TOTALS", date_range_type="CUSTOM", group_by="TAG",
            date_from=date(2025, 1, 1), date_to=date(2025, 12, 31),
            account_ids=[], tag_selections=[], show_transactions=False,
            show_subtotal=False, include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("-100.00")

    def test_archived_included_by_default(self, account, archived_status, tx_type, tag):
        _make_tx(account, archived_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        result = run_report(
            report_type="TOTALS", date_range_type="CUSTOM", group_by="TAG",
            date_from=date(2025, 1, 1), date_to=date(2025, 12, 31),
            account_ids=[], tag_selections=[], show_transactions=False,
            show_subtotal=False, include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("-100.00")

    def test_pending_excluded_by_default(self, account, pending_status, tx_type, tag):
        _make_tx(account, pending_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        result = run_report(
            report_type="TOTALS", date_range_type="CUSTOM", group_by="TAG",
            date_from=date(2025, 1, 1), date_to=date(2025, 12, 31),
            account_ids=[], tag_selections=[], show_transactions=False,
            show_subtotal=False, include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("0.00")

    def test_pending_included_when_flag_set(self, account, pending_status, tx_type, tag):
        _make_tx(account, pending_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        result = run_report(
            report_type="TOTALS", date_range_type="CUSTOM", group_by="TAG",
            date_from=date(2025, 1, 1), date_to=date(2025, 12, 31),
            account_ids=[], tag_selections=[], show_transactions=False,
            show_subtotal=False, include_pending=True,
        )
        assert result["rows"][0]["total"] == Decimal("-100.00")

    def test_all_statuses_combined(
        self, account, cleared_status, pending_status, reconciled_status, archived_status, tx_type, tag
    ):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-10.00"), tag)
        _make_tx(account, pending_status, tx_type, JAN_1, Decimal("-20.00"), tag)
        _make_tx(account, reconciled_status, tx_type, JAN_1, Decimal("-30.00"), tag)
        _make_tx(account, archived_status, tx_type, JAN_1, Decimal("-40.00"), tag)

        result = run_report(
            report_type="TOTALS", date_range_type="CUSTOM", group_by="TAG",
            date_from=date(2025, 1, 1), date_to=date(2025, 12, 31),
            account_ids=[], tag_selections=[], show_transactions=False,
            show_subtotal=False, include_pending=True,
        )
        assert result["rows"][0]["total"] == Decimal("-100.00")


# ---------------------------------------------------------------------------
# Service: account filtering
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.service
class TestAccountFiltering:
    def test_account_filter_excludes_other_accounts(
        self, account, other_account, cleared_status, tx_type, tag
    ):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(other_account, cleared_status, tx_type, JAN_1, Decimal("-999.00"), tag)

        result = run_report(
            report_type="TOTALS", date_range_type="CUSTOM", group_by="TAG",
            date_from=date(2025, 1, 1), date_to=date(2025, 12, 31),
            account_ids=[account.id], tag_selections=[], show_transactions=False,
            show_subtotal=False, include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("-100.00")

    def test_empty_account_ids_includes_all(
        self, account, other_account, cleared_status, tx_type, tag
    ):
        _make_tx(account, cleared_status, tx_type, JAN_1, Decimal("-100.00"), tag)
        _make_tx(other_account, cleared_status, tx_type, JAN_1, Decimal("-50.00"), tag)

        result = run_report(
            report_type="TOTALS", date_range_type="CUSTOM", group_by="TAG",
            date_from=date(2025, 1, 1), date_to=date(2025, 12, 31),
            account_ids=[], tag_selections=[], show_transactions=False,
            show_subtotal=False, include_pending=False,
        )
        assert result["rows"][0]["total"] == Decimal("-150.00")
