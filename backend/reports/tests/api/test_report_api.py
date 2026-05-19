import pytest
from datetime import date
from decimal import Decimal

from accounts.models import Account, AccountType, Bank
from tags.models import MainTag, SubTag, Tag, TagType
from transactions.models import Transaction, TransactionDetail, TransactionStatus, TransactionType
from reports.models import ReportConfig, ReportConfigTag

AUTH = {"Authorization": "Bearer test-api-key"}


# ---------------------------------------------------------------------------
# Shared helpers / fixtures
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
def test_tag(main_tag, sub_tag, tag_type):
    return Tag.objects.create(parent=main_tag, child=sub_tag, tag_type=tag_type)


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
def cleared_status(db):
    return TransactionStatus.objects.create(transaction_status="Cleared")


@pytest.fixture
def tx_type(db):
    return TransactionType.objects.create(transaction_type="Expense")


@pytest.fixture
def existing_config(db):
    return ReportConfig.objects.create(
        name="Saved Report",
        report_type="TOTALS",
        date_range_type="THIS_YEAR",
        group_by="TAG",
    )


def _config_payload(**overrides):
    base = {
        "name": "Tax Report",
        "description": "Annual tax summary",
        "report_type": "TOTALS",
        "date_range_type": "THIS_YEAR",
        "date_from": None,
        "date_to": None,
        "account_ids": [],
        "group_by": "TAG",
        "show_transactions": False,
        "show_subtotal": True,
        "include_pending": False,
        "tag_selections": [],
    }
    base.update(overrides)
    return base


def _run_payload(**overrides):
    base = {
        "report_type": "TOTALS",
        "date_range_type": "CUSTOM",
        "date_from": "2025-01-01",
        "date_to": "2025-12-31",
        "account_ids": [],
        "group_by": "TAG",
        "show_transactions": False,
        "show_subtotal": True,
        "include_pending": False,
        "tag_selections": [],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
class TestListReports:
    def test_empty_list(self, api_client):
        response = api_client.get("/reports", headers=AUTH)
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_configs(self, api_client, existing_config):
        response = api_client.get("/reports", headers=AUTH)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Saved Report"


@pytest.mark.django_db
@pytest.mark.api
class TestCreateReport:
    def test_create_minimal(self, api_client):
        response = api_client.post("/reports", json=_config_payload(), headers=AUTH)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Tax Report"
        assert data["report_type"] == "TOTALS"
        assert data["group_by"] == "TAG"
        assert data["id"] is not None

    def test_create_with_tag_selection(self, api_client, test_tag):
        payload = _config_payload(
            tag_selections=[{"tag_id": test_tag.id, "sub_tag_id": None, "main_tag_id": None}]
        )
        response = api_client.post("/reports", json=payload, headers=AUTH)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tag_selections"]) == 1
        assert data["tag_selections"][0]["tag_id"] == test_tag.id

    def test_create_with_account_filter(self, api_client, account):
        payload = _config_payload(account_ids=[account.id])
        response = api_client.post("/reports", json=payload, headers=AUTH)
        assert response.status_code == 200
        assert account.id in response.json()["account_ids"]

    def test_create_invalid_tag_selection_two_set(self, api_client, test_tag, main_tag):
        payload = _config_payload(
            tag_selections=[{"tag_id": test_tag.id, "sub_tag_id": None, "main_tag_id": main_tag.id}]
        )
        response = api_client.post("/reports", json=payload, headers=AUTH)
        assert response.status_code == 400

    def test_create_stored_in_db(self, api_client):
        api_client.post("/reports", json=_config_payload(), headers=AUTH)
        assert ReportConfig.objects.filter(name="Tax Report").exists()


@pytest.mark.django_db
@pytest.mark.api
class TestGetReport:
    def test_get_existing(self, api_client, existing_config):
        response = api_client.get(f"/reports/{existing_config.id}", headers=AUTH)
        assert response.status_code == 200
        assert response.json()["id"] == existing_config.id

    def test_get_not_found(self, api_client):
        response = api_client.get("/reports/99999", headers=AUTH)
        assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
class TestUpdateReport:
    def test_update_name(self, api_client, existing_config):
        payload = _config_payload(name="Updated Name")
        response = api_client.put(f"/reports/{existing_config.id}", json=payload, headers=AUTH)
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"
        existing_config.refresh_from_db()
        assert existing_config.name == "Updated Name"

    def test_update_tag_selections_replaces_existing(self, api_client, existing_config, test_tag):
        ReportConfigTag.objects.create(report=existing_config, main_tag_id=1)
        payload = _config_payload(
            tag_selections=[{"tag_id": test_tag.id, "sub_tag_id": None, "main_tag_id": None}]
        )
        response = api_client.put(f"/reports/{existing_config.id}", json=payload, headers=AUTH)
        assert response.status_code == 200
        sels = response.json()["tag_selections"]
        assert len(sels) == 1
        assert sels[0]["tag_id"] == test_tag.id

    def test_update_not_found(self, api_client):
        response = api_client.put("/reports/99999", json=_config_payload(), headers=AUTH)
        assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
class TestDeleteReport:
    def test_delete_existing(self, api_client, existing_config):
        config_id = existing_config.id
        response = api_client.delete(f"/reports/{config_id}", headers=AUTH)
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert not ReportConfig.objects.filter(id=config_id).exists()

    def test_delete_not_found(self, api_client):
        response = api_client.delete("/reports/99999", headers=AUTH)
        assert response.status_code == 404


# ---------------------------------------------------------------------------
# Ad-hoc run
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
class TestRunAdhocReport:
    def test_run_returns_result_shape(self, api_client, cleared_status):
        response = api_client.post("/reports/run", json=_run_payload(), headers=AUTH)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "TOTALS"
        assert data["group_by"] == "TAG"
        assert "rows" in data
        assert "date_from" in data
        assert "date_to" in data

    def test_run_invalid_report_type(self, api_client):
        payload = _run_payload(report_type="INVALID")
        response = api_client.post("/reports/run", json=payload, headers=AUTH)
        assert response.status_code == 400

    def test_run_invalid_group_by(self, api_client):
        payload = _run_payload(group_by="PAYEE")
        response = api_client.post("/reports/run", json=payload, headers=AUTH)
        assert response.status_code == 400

    def test_run_custom_range_missing_dates(self, api_client):
        payload = _run_payload(date_range_type="CUSTOM", date_from=None, date_to=None)
        response = api_client.post("/reports/run", json=payload, headers=AUTH)
        assert response.status_code == 400

    def test_run_comparison_type(self, api_client, cleared_status):
        payload = _run_payload(report_type="COMPARISON")
        response = api_client.post("/reports/run", json=payload, headers=AUTH)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "COMPARISON"
        assert data["period2_from"] is not None

    def test_run_with_transactions_in_range(
        self, api_client, account, cleared_status, tx_type, test_tag
    ):
        tx = Transaction.objects.create(
            source_account=account,
            status=cleared_status,
            transaction_type=tx_type,
            transaction_date=date(2025, 3, 15),
            total_amount=Decimal("-75.00"),
            description="Groceries run",
        )
        TransactionDetail.objects.create(transaction=tx, detail_amt=Decimal("-75.00"), tag=test_tag)

        response = api_client.post("/reports/run", json=_run_payload(), headers=AUTH)
        assert response.status_code == 200
        rows = response.json()["rows"]
        assert len(rows) == 1
        assert Decimal(str(rows[0]["total"])) == Decimal("-75.00")

    def test_run_show_subtotal_true(self, api_client, cleared_status):
        response = api_client.post("/reports/run", json=_run_payload(show_subtotal=True), headers=AUTH)
        assert response.status_code == 200
        data = response.json()
        assert data.get("subtotal") is not None or data.get("subtotal") == 0

    def test_run_month_groupby(self, api_client, cleared_status):
        payload = _run_payload(
            group_by="MONTH",
            date_from="2025-01-01",
            date_to="2025-03-31",
        )
        response = api_client.post("/reports/run", json=payload, headers=AUTH)
        assert response.status_code == 200
        rows = response.json()["rows"]
        labels = [r["label"] for r in rows]
        assert "January 2025" in labels
        assert "March 2025" in labels


# ---------------------------------------------------------------------------
# Saved config run
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
class TestRunSavedReport:
    def test_run_saved_config(self, api_client, existing_config, cleared_status):
        response = api_client.post(f"/reports/{existing_config.id}/run", headers=AUTH)
        assert response.status_code == 200
        data = response.json()
        assert data["report_type"] == "TOTALS"
        assert "rows" in data

    def test_run_saved_config_not_found(self, api_client):
        response = api_client.post("/reports/99999/run", headers=AUTH)
        assert response.status_code == 404

    def test_run_saved_config_with_tag_selection(
        self, api_client, account, cleared_status, tx_type, test_tag
    ):
        config = ReportConfig.objects.create(
            name="Tag Report",
            report_type="TOTALS",
            date_range_type="CUSTOM",
            date_from=date(2025, 1, 1),
            date_to=date(2025, 12, 31),
            group_by="TAG",
        )
        ReportConfigTag.objects.create(report=config, tag=test_tag)

        tx = Transaction.objects.create(
            source_account=account,
            status=cleared_status,
            transaction_type=tx_type,
            transaction_date=date(2025, 6, 1),
            total_amount=Decimal("-50.00"),
            description="Tagged tx",
        )
        TransactionDetail.objects.create(transaction=tx, detail_amt=Decimal("-50.00"), tag=test_tag)

        response = api_client.post(f"/reports/{config.id}/run", headers=AUTH)
        assert response.status_code == 200
        rows = response.json()["rows"]
        assert len(rows) == 1
        assert Decimal(str(rows[0]["total"])) == Decimal("-50.00")
