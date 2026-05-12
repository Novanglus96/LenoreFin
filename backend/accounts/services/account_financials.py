from datetime import date
from accounts.models import Account, Reward
from utils.dates import get_todays_date_timezone_adjusted
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.db.models import (
    Subquery,
    OuterRef,
    Max,
)
from django.db.models.functions import TruncMonth
from datetime import timedelta
from transactions.services import (
    get_account_cleared_balance,
    get_account_pending_balance,
)
from accounts.dto import DomainAccount, DomainBank, DomainAccountType
from core.dto.utils import dto_from_model
from django.core.cache import cache
from core.cache.keys import account_financials
from accounts.api.schemas.account import (
    AccountQuery,
)


class AccountNotFound(Exception):
    pass


def get_account_financials(account_id: int, today: date | None = None):
    """
    Returns an Account annotated with all calculated financial fields.
    """
    # Check Cache
    key = account_financials(account_id)
    data = cache.get(key)
    if data:
        return data

    today = today or get_todays_date_timezone_adjusted()

    qs = Account.objects.filter(id=account_id)
    if not qs.exists():
        raise AccountNotFound()

    account = qs.first()

    # Calcuate due/statement dates
    due_date = (
        today.replace(day=1) + relativedelta(day=account.due_day)
        if account.due_day > today.day
        else today.replace(day=1) + relativedelta(months=1, day=account.due_day)
    )

    statement_date = (
        today.replace(day=1) + relativedelta(day=account.statement_day)
        if account.statement_day > today.day
        else today.replace(day=1)
        + relativedelta(months=1, day=account.statement_day)
    )

    # Get rewards amount for account
    rewards_total_object = (
        Reward.objects.filter(reward_account_id=account_id)
        .order_by("-reward_date", "-id")
        .first()
    )
    rewards_amount = (
        rewards_total_object.reward_amount
        if rewards_total_object
        else Decimal("0.00")
    )

    # Cleared Balance
    cleared_balance = get_account_cleared_balance(account_id)

    # Pending Balance
    pending_balance = get_account_pending_balance(account_id)

    # Available Credit
    available_credit = account.credit_limit - abs(pending_balance)

    financials = DomainAccount(
        id=account.id,
        account_name=account.account_name,
        account_type=dto_from_model(DomainAccountType, account.account_type),
        opening_balance=account.opening_balance,
        annual_rate=account.annual_rate,
        active=account.active,
        open_date=account.open_date,
        bank=dto_from_model(DomainBank, account.bank),
        current_yr_rewards=last_six_month_reward_amounts(account_id),
        last_yr_rewards=last_year_six_month_reward_amounts(account_id),
        due_date=due_date,
        statement_date=statement_date,
        statement_cycle_length=account.statement_cycle_length,
        statement_cycle_period=account.statement_cycle_period,
        credit_limit=account.credit_limit,
        rewards_amount=rewards_amount,
        available_credit=available_credit,
        balance=cleared_balance,
        statement_balance=account.statement_balance,
        funding_account=dto_from_model(DomainAccount, account.funding_account),
        calculate_payments=account.calculate_payments,
        calculate_interest=account.calculate_interest,
        payment_strategy=account.payment_strategy,
        payment_amount=account.payment_amount,
        minimum_payment_amount=account.minimum_payment_amount,
        statement_day=account.statement_day,
        due_day=account.due_day,
        pay_day=account.pay_day,
        interest_deposit_day=account.interest_deposit_day,
    )

    cache.set(key, financials, timeout=60 * 60)
    return financials


def last_six_month_reward_amounts(account_id: int):
    today = get_todays_date_timezone_adjusted()
    first_of_current_month = today.replace(day=1)

    # --- Build the last 6 months (newest first) ---
    months = []
    current = first_of_current_month
    for _ in range(5):
        months.append(current)
        prev = (current - timedelta(days=1)).replace(day=1)
        current = prev

    # --- Build queryset for last reward per month ---
    base = Reward.objects.filter(reward_account__id=account_id).annotate(
        month=TruncMonth("reward_date")
    )

    sub = (
        base.values("month")
        .annotate(last_date=Max("reward_date"))
        .filter(month=OuterRef("month"))
    )

    latest = base.filter(reward_date=Subquery(sub.values("last_date")))

    # Convert queryset to lookup dictionary {month: amount}
    latest_lookup = {row.month: row.reward_amount for row in latest}

    # --- Build final list of amounts (0 for missing months) ---
    amounts = [latest_lookup.get(month, 0) for month in months]
    amounts = list(reversed(amounts))

    return amounts


def last_year_six_month_reward_amounts(account_id: int):
    today = get_todays_date_timezone_adjusted()

    # Move 1 year back
    last_year_today = today.replace(year=today.year - 1)
    first_of_target_month = last_year_today.replace(day=1)

    # --- Build the 6 months for last year (newest → oldest) ---
    months = []
    current = first_of_target_month
    for _ in range(5):
        months.append(current)
        prev = (current - timedelta(days=1)).replace(day=1)
        current = prev

    # --- Query for the latest reward entry per month ---
    base = Reward.objects.filter(reward_account__id=account_id).annotate(
        month=TruncMonth("reward_date")
    )

    sub = (
        base.values("month")
        .annotate(last_date=Max("reward_date"))
        .filter(month=OuterRef("month"))
    )

    latest = base.filter(reward_date=Subquery(sub.values("last_date")))

    # Build lookup dictionary: {month: reward_amount}
    latest_lookup = {row.month: row.reward_amount for row in latest}

    # Build newest → oldest
    newest_to_oldest = [latest_lookup.get(month, 0) for month in months]

    # Reverse → oldest → newest
    oldest_to_newest = list(reversed(newest_to_oldest))

    return oldest_to_newest


def list_accounts_with_financials(query: AccountQuery) -> list[DomainAccount]:
    account_list = []

    # Retrieve all accounts
    qs = Account.objects.all()

    # If inactive argument is provided, filter by active/inactive
    if not query.inactive:
        qs = qs.filter(active=True)

    # If account type argument is provided, filter by account type
    if query.account_type is not None and query.account_type != 0:
        qs = qs.filter(account_type__id=query.account_type)

    if query.account_type is not None and query.account_type == 0:
        qs = qs.filter(active=False)

    # Order accounts by account type id ascending, bank name ascending, and account
    # name ascending
    qs = qs.order_by("account_type__id", "bank__bank_name", "account_name")

    # Get Account financials
    for account in qs:
        result = get_account_financials(account.id)

        account_list.append(result)

    return account_list
