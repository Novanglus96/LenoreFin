from accounts.dto import DomainAccount, DomainAccountType, DomainBank
from accounts.api.schemas.account import AccountOut
from accounts.api.schemas.bank import BankOut
from accounts.api.schemas.account_type import AccountTypeOut


def domain_bank_to_schema(
    bank: DomainBank,
) -> BankOut:
    if bank is not None:
        return BankOut(id=bank.id, bank_name=bank.bank_name)
    else:
        return None


def domain_account_type_to_schema(
    account_type: DomainAccountType,
) -> AccountTypeOut:
    if account_type is not None:
        return AccountTypeOut(
            id=account_type.id,
            account_type=account_type.account_type,
            color=account_type.color,
            icon=account_type.icon,
        )
    else:
        return None


def domain_account_to_schema(
    account: DomainAccount,
) -> AccountOut:
    if account is not None:
        return AccountOut(
            id=account.id,
            account_name=account.account_name,
            account_type=domain_account_type_to_schema(account.account_type),
            opening_balance=account.opening_balance,
            annual_rate=account.annual_rate,
            due_date=account.due_date,
            active=account.active,
            open_date=account.open_date,
            statement_date=account.statement_date,
            statement_cycle_length=account.statement_cycle_length,
            statement_cycle_period=account.statement_cycle_period,
            credit_limit=account.credit_limit,
            rewards_amount=account.rewards_amount,
            available_credit=account.available_credit,
            balance=account.balance,
            bank=domain_bank_to_schema(account.bank),
            last_statement_amount=account.last_statement_amount,
            funding_account=domain_account_to_schema(account.funding_account),
            calculate_payments=account.calculate_payments,
            calculate_interest=account.calculate_interest,
            payment_strategy=account.payment_strategy,
            payment_amount=account.payment_amount,
            minimum_payment_amount=account.minimum_payment_amount,
            statement_day=account.statement_day,
            due_day=account.due_day,
            pay_day=account.pay_day,
            current_yr_rewards=account.current_yr_rewards,
            last_yr_rewards=account.last_yr_rewards,
        )
    else:
        return None
