import pytest
from transactions.models import TransactionType
from django.db import IntegrityError


@pytest.mark.django_db
def test_transaction_type_creation(test_expense_transaction_type):
    assert test_expense_transaction_type.id is not None
    assert test_expense_transaction_type.transaction_type == "Expense"


@pytest.mark.django_db
def test_transaction_type_string_representation(test_expense_transaction_type):
    expected = "Expense"
    assert test_expense_transaction_type.id is not None
    assert str(test_expense_transaction_type == expected)


@pytest.mark.django_db
def test_transaction_type_uniqueness(test_expense_transaction_type):
    with pytest.raises(IntegrityError):
        TransactionType.objects.create(transaction_type="Expense")
