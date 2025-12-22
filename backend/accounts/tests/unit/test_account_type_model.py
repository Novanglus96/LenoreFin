import pytest
from accounts.models import AccountType


@pytest.mark.django_db
@pytest.mark.unit
def test_account_type_creation():
    account_type = AccountType.objects.create(
        account_type="Checking", color="#059669", icon="mdi-checkbook"
    )

    assert account_type.id is not None
    assert account_type.account_type == "Checking"
    assert account_type.color == "#059669"
    assert account_type.icon == "mdi-checkbook"


@pytest.mark.django_db
@pytest.mark.unit
def test_account_type_default_color():
    account_type = AccountType.objects.create(
        account_type="Checking", icon="mdi-checkbook"
    )

    assert account_type.color == "#059669"


@pytest.mark.django_db
@pytest.mark.unit
def test_account_type_string_representation():
    """Ensure __str__ returns the expected formatted string."""
    account_type = AccountType.objects.create(
        account_type="Checking", color="#059669", icon="mdi-checkbook"
    )

    expected = "Checking"
    assert str(account_type) == expected


@pytest.mark.django_db
@pytest.mark.unit
def test_account_type_foreign_key_null_delete(
    test_checking_account, checking_account_type
):
    """AccountType should set account_type to NULL when deleted."""

    # Delete the AccountType
    checking_account_type.delete()

    # Refresh the Account instance from DB
    test_checking_account.refresh_from_db()

    # Now Django has updated the foreign key to NULL
    assert test_checking_account.account_type is None
