import pytest
from decimal import Decimal
from accounts.services import get_account_financials, list_accounts_with_financials, AccountNotFound
from accounts.dto import DomainAccount
from accounts.api.schemas.account import AccountQuery


@pytest.mark.django_db
@pytest.mark.service
def test_get_account_financials_returns_domain_account(test_checking_account):
    result = get_account_financials(test_checking_account.id)

    assert isinstance(result, DomainAccount)
    assert result.id == test_checking_account.id
    assert result.account_name == test_checking_account.account_name
    assert result.opening_balance == Decimal(str(test_checking_account.opening_balance))


@pytest.mark.django_db
@pytest.mark.service
def test_get_account_financials_raises_for_missing_account():
    with pytest.raises(AccountNotFound):
        get_account_financials(9999)


@pytest.mark.django_db
@pytest.mark.service
def test_get_account_financials_includes_computed_dates(test_checking_account):
    result = get_account_financials(test_checking_account.id)

    assert result.due_date is not None
    assert result.statement_date is not None


@pytest.mark.django_db
@pytest.mark.service
def test_list_accounts_with_financials_active_only(
    test_checking_account,
    test_savings_account,
    test_credit_card_account,
):
    test_credit_card_account.active = False
    test_credit_card_account.save()

    query = AccountQuery(inactive=False, account_type=None)
    result = list_accounts_with_financials(query)

    assert len(result) == 2
    names = [a.account_name for a in result]
    assert test_checking_account.account_name in names
    assert test_savings_account.account_name in names
    assert test_credit_card_account.account_name not in names


@pytest.mark.django_db
@pytest.mark.service
def test_list_accounts_with_financials_includes_inactive(
    test_checking_account,
    test_savings_account,
    test_credit_card_account,
):
    test_credit_card_account.active = False
    test_credit_card_account.save()

    query = AccountQuery(inactive=True, account_type=None)
    result = list_accounts_with_financials(query)

    assert len(result) == 3


@pytest.mark.django_db
@pytest.mark.service
def test_list_accounts_with_financials_filter_by_type(
    test_checking_account,
    test_savings_account,
    checking_account_type,
):
    query = AccountQuery(inactive=False, account_type=checking_account_type.id)
    result = list_accounts_with_financials(query)

    assert len(result) == 1
    assert result[0].account_name == test_checking_account.account_name
