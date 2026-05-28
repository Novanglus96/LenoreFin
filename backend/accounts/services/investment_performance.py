from decimal import Decimal, InvalidOperation
from datetime import date

from dateutil.relativedelta import relativedelta
from django.db.models import Q

from accounts.models import Account
from transactions.models import Transaction, TransactionStatus


def _signed_amount(tx, account_id: int) -> Decimal:
    """Amount from this account's perspective: incoming = positive, outgoing = raw (negative)."""
    if tx.destination_account_id == account_id:
        return abs(tx.total_amount)
    return tx.total_amount


def calculate_investment_return(account_id: int, months: int = 12) -> dict | None:
    """
    Modified Dietz return for an investment account over the last `months` months.

    Returns None when the account isn't an investment type, has no cleared history,
    or the measurement window is too short to be meaningful.

    Return dict: {rate (annualised % float), period_months, data_points}
    """
    try:
        account = Account.objects.select_related("account_type").get(pk=account_id)
    except Account.DoesNotExist:
        return None

    if account.account_type.slug != "investment":
        return None

    try:
        cleared_status = TransactionStatus.objects.get(slug="cleared")
    except TransactionStatus.DoesNotExist:
        return None

    today = date.today()
    start_date = today - relativedelta(months=months)
    total_days = (today - start_date).days

    if total_days < 30:
        return None

    account_q = Q(source_account_id=account_id) | Q(destination_account_id=account_id)

    # --- Beginning Market Value (all cleared txs strictly before period start) ---
    pre_txs = Transaction.objects.filter(
        account_q,
        status=cleared_status,
        transaction_date__lt=start_date,
    ).select_related("transaction_type")

    bmv = account.opening_balance + account.archive_balance
    for tx in pre_txs:
        bmv += _signed_amount(tx, account_id)

    # --- Ending Market Value (all cleared txs up to today) ---
    emv = account.opening_balance + account.archive_balance
    all_cleared = Transaction.objects.filter(
        account_q,
        status=cleared_status,
        transaction_date__lte=today,
    ).select_related("transaction_type")
    for tx in all_cleared:
        emv += _signed_amount(tx, account_id)

    # --- Period transactions (for data_points count and cash-flow weighting) ---
    period_txs = Transaction.objects.filter(
        account_q,
        status=cleared_status,
        transaction_date__gte=start_date,
        transaction_date__lte=today,
    ).select_related("transaction_type").order_by("transaction_date")

    data_points = period_txs.count()
    if data_points == 0:
        return None

    # --- Cash flows: only external transfers (money moving in/out from other accounts) ---
    # Income/expense transactions are intrinsic returns (dividends, fees) — excluded from CF.
    net_cf = Decimal("0")
    weighted_cf = Decimal("0")
    for tx in period_txs:
        if tx.transaction_type and tx.transaction_type.slug == "transfer":
            cf = _signed_amount(tx, account_id)
            days_remaining = (today - tx.transaction_date).days
            weight = Decimal(days_remaining) / Decimal(total_days)
            net_cf += cf
            weighted_cf += cf * weight

    # --- Modified Dietz ---
    denominator = bmv + weighted_cf
    if denominator == 0:
        return None

    try:
        period_return = (emv - bmv - net_cf) / denominator
        # Annualise: (1 + R)^(365/days) - 1
        annualized = (Decimal("1") + period_return) ** (
            Decimal("365") / Decimal(total_days)
        ) - Decimal("1")
        rate = float(annualized * 100)
    except (InvalidOperation, ZeroDivisionError, OverflowError):
        return None

    # Sanity-check: clamp extreme values that indicate bad data
    if abs(rate) > 1000:
        return None

    return {
        "rate": round(rate, 2),
        "period_months": months,
        "data_points": data_points,
    }
