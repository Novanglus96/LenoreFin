import pytest
from django.utils import timezone
import pytz
import os

from transactions.models import Transaction, TransactionDetail

AUTH = {"Authorization": "Bearer test-api-key"}

# test_income_transaction_type is requested by every creating test because
# create_transactions looks up the "income" TransactionType by slug to decide
# the sign, and blows up with a 500 if that row is missing.


def current_date():
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    return today.astimezone(tz_timezone).date()


def build_payload(
    account,
    transaction_type,
    status,
    *,
    amount="10.00",
    description="Batch row",
    tag=None,
    destination_account=None,
):
    """Build one TransactionIn dict the way the multi-add form does."""
    today = current_date().isoformat()
    payload = {
        "transaction_date": today,
        "total_amount": amount,
        "status_id": status.id,
        "description": description,
        "edit_date": today,
        "add_date": today,
        "transaction_type_id": transaction_type.id,
        "source_account_id": account.id,
        "destination_account_id": (
            destination_account.id if destination_account else None
        ),
        "details": None,
    }
    if tag is not None:
        # The form always tags the full row amount, so full_toggle is on.
        payload["details"] = [
            {
                "tag_id": tag.id,
                "tag_amt": amount,
                "tag_pretty_name": tag.tag_name,
                "tag_full_toggle": True,
            }
        ]
    return payload


@pytest.mark.django_db
@pytest.mark.api
def test_create_multiple_transactions(
    api_client,
    test_checking_account,
    test_expense_transaction_type,
    test_income_transaction_type,
    test_pending_transaction_status,
):
    response = api_client.post(
        "/transactions/create-multiple",
        json={
            "transactions": [
                build_payload(
                    test_checking_account,
                    test_expense_transaction_type,
                    test_pending_transaction_status,
                    amount="12.34",
                    description="Groceries",
                ),
                build_payload(
                    test_checking_account,
                    test_expense_transaction_type,
                    test_pending_transaction_status,
                    amount="56.78",
                    description="Gas",
                ),
            ]
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["created"] == 2

    created = Transaction.objects.filter(
        description__in=["Groceries", "Gas"]
    ).order_by("description")
    assert created.count() == 2
    # Expenses are stored negative regardless of the sign that was sent.
    assert [str(t.total_amount) for t in created] == ["-56.78", "-12.34"]


@pytest.mark.django_db
@pytest.mark.api
def test_create_multiple_derives_sign_per_row_type(
    api_client,
    test_checking_account,
    test_expense_transaction_type,
    test_income_transaction_type,
    test_pending_transaction_status,
):
    """Each row's sign comes from its own transaction type, not the batch's."""
    response = api_client.post(
        "/transactions/create-multiple",
        json={
            "transactions": [
                build_payload(
                    test_checking_account,
                    test_expense_transaction_type,
                    test_pending_transaction_status,
                    amount="20.00",
                    description="An expense row",
                ),
                build_payload(
                    test_checking_account,
                    test_income_transaction_type,
                    test_pending_transaction_status,
                    amount="30.00",
                    description="An income row",
                ),
            ]
        },
        headers=AUTH,
    )

    assert response.status_code == 200

    expense = Transaction.objects.get(description="An expense row")
    income = Transaction.objects.get(description="An income row")
    assert str(expense.total_amount) == "-20.00"
    assert str(income.total_amount) == "30.00"


@pytest.mark.django_db
@pytest.mark.api
def test_create_multiple_creates_tag_details(
    api_client,
    test_checking_account,
    test_expense_transaction_type,
    test_income_transaction_type,
    test_pending_transaction_status,
    test_tag,
):
    response = api_client.post(
        "/transactions/create-multiple",
        json={
            "transactions": [
                build_payload(
                    test_checking_account,
                    test_expense_transaction_type,
                    test_pending_transaction_status,
                    amount="45.00",
                    description="Tagged row",
                    tag=test_tag,
                )
            ]
        },
        headers=AUTH,
    )

    assert response.status_code == 200

    created = Transaction.objects.get(description="Tagged row")
    detail = TransactionDetail.objects.get(transaction_id=created.id)
    assert detail.tag_id == test_tag.id
    assert detail.full_toggle is True
    # full_toggle means the detail covers the whole (negative) row amount.
    assert str(detail.detail_amt) == "-45.00"


@pytest.mark.django_db
@pytest.mark.api
def test_create_multiple_rejects_empty_batch(api_client):
    response = api_client.post(
        "/transactions/create-multiple",
        json={"transactions": []},
        headers=AUTH,
    )

    assert response.status_code == 400
    assert Transaction.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.api
def test_create_multiple_rejects_parent_account(
    api_client,
    test_checking_account,
    test_savings_account,
    test_expense_transaction_type,
    test_pending_transaction_status,
):
    """A parent account is not postable, and it fails the whole batch."""
    test_savings_account.parent_account = test_checking_account
    test_savings_account.save()

    response = api_client.post(
        "/transactions/create-multiple",
        json={
            "transactions": [
                build_payload(
                    test_savings_account,
                    test_expense_transaction_type,
                    test_pending_transaction_status,
                    description="Fine row",
                ),
                build_payload(
                    test_checking_account,
                    test_expense_transaction_type,
                    test_pending_transaction_status,
                    description="Parent row",
                ),
            ]
        },
        headers=AUTH,
    )

    assert response.status_code == 400
    # The valid row must not have been created either.
    assert not Transaction.objects.filter(description="Fine row").exists()


@pytest.mark.django_db
@pytest.mark.api
def test_create_multiple_is_atomic(
    api_client,
    test_checking_account,
    test_expense_transaction_type,
    test_pending_transaction_status,
    monkeypatch,
):
    """A failure part-way through leaves nothing behind, not even the earlier rows."""
    monkeypatch.setattr(
        "transactions.services.transaction.create_transactions",
        lambda *args, **kwargs: False,
    )

    response = api_client.post(
        "/transactions/create-multiple",
        json={
            "transactions": [
                build_payload(
                    test_checking_account,
                    test_expense_transaction_type,
                    test_pending_transaction_status,
                    description="Rolled back row",
                )
            ]
        },
        headers=AUTH,
    )

    assert response.status_code == 500
    assert not Transaction.objects.filter(description="Rolled back row").exists()
    # The description history written while building the batch rolls back too.
    from administration.models import DescriptionHistory

    assert not DescriptionHistory.objects.filter(
        description_normalized="rolled back row"
    ).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_create_multiple_supports_transfers(
    api_client,
    test_checking_account,
    test_savings_account,
    test_transfer_transaction_type,
    test_income_transaction_type,
    test_pending_transaction_status,
):
    response = api_client.post(
        "/transactions/create-multiple",
        json={
            "transactions": [
                build_payload(
                    test_checking_account,
                    test_transfer_transaction_type,
                    test_pending_transaction_status,
                    amount="100.00",
                    description="Move to savings",
                    destination_account=test_savings_account,
                )
            ]
        },
        headers=AUTH,
    )

    assert response.status_code == 200

    created = Transaction.objects.get(description="Move to savings")
    assert created.source_account_id == test_checking_account.id
    assert created.destination_account_id == test_savings_account.id
