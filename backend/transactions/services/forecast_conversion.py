import re

from django.db import transaction as db_transaction
from django.db.models import Q

from core.broadcast import broadcast_invalidate
from core.cache.helpers import delete_pattern
from core.cache.keys import account_all
from tags.api.dependencies.custom_tag import CustomTag
from transactions.api.dependencies.create_transactions import create_transactions
from transactions.api.dependencies.full_transaction import FullTransaction
from transactions.models import (
    ForecastCacheTransaction,
    ForecastCacheTransactionDetail,
    TransactionStatus,
)
from utils.dates import get_todays_date_timezone_adjusted


class ForecastTransactionNotFound(Exception):
    pass


def clean_forecast_description(description: str) -> str:
    """
    Turns a projected description into one that reads as a real transaction.

    The forecast generators label their rows "({name} Estimated Payment)" and
    "({name} Estimated Interest)" -- the brackets and the word "Estimated" mark
    the row as a projection. Once converted the transaction is real, so both
    markers are dropped: "(Visa Estimated Payment)" becomes "Visa Payment".

    Leaves anything that does not carry those markers untouched.
    """

    if not description:
        return description

    text = description.strip()
    if text.startswith("(") and text.endswith(")"):
        text = text[1:-1]
    text = re.sub(r"\bestimated\b", "", text, flags=re.IGNORECASE)
    # Collapse the gap the removed word leaves behind.
    return " ".join(text.split())


def convert_forecast_transaction(forecast_id: int) -> None:
    """
    Materialises a computed forecast row into a real pending Transaction.

    ForecastCacheTransactions are projections derived from account settings
    (credit-card statement interest/payments, savings interest) rather than
    instances of a Reminder, so unlike ReminderCacheTransaction they carry no
    reminder FK and cannot go through add_reminder_transaction. This copies the
    row across — amount, dates, accounts and tags — and drops the cache entry so
    the table reflects the change immediately. The only field not carried
    verbatim is the description, which loses its projection markers (see
    clean_forecast_description).

    The cache row is safe to delete because the generators rebuild it: the
    credit-card payment forecast subtracts existing real and reminder
    transactions in the payment window from the cycle payment, so once this
    transaction exists the row is regenerated smaller or not at all.

    Args:
        forecast_id (int): id of the ForecastCacheTransaction to convert.

    Raises:
        ForecastTransactionNotFound: if no such forecast transaction exists.
    """

    try:
        forecast = ForecastCacheTransaction.objects.get(id=forecast_id)
    except ForecastCacheTransaction.DoesNotExist:
        raise ForecastTransactionNotFound(
            f"Forecast transaction {forecast_id} not found"
        )

    today = get_todays_date_timezone_adjusted()
    pending_status_id = TransactionStatus.objects.values_list(
        "id", flat=True
    ).get(slug="pending")

    # create_transactions re-derives the sign and the full-toggle amounts from
    # transaction_type, so the stored (already signed) values are passed as
    # magnitudes and come back out identical.
    tags = [
        CustomTag(
            tag_name=None,
            tag_amount=abs(detail.detail_amt),
            tag_id=detail.tag_id,
            tag_full_toggle=detail.full_toggle,
        )
        for detail in ForecastCacheTransactionDetail.objects.filter(
            transaction_id=forecast.id
        )
        if detail.tag_id is not None
    ]

    new_transaction = FullTransaction(
        transaction_date=forecast.transaction_date,
        total_amount=forecast.total_amount,
        status_id=pending_status_id,
        memo=forecast.memo,
        description=clean_forecast_description(forecast.description),
        edit_date=today,
        add_date=today,
        transaction_type_id=forecast.transaction_type_id,
        paycheck_id=forecast.paycheck_id,
        source_account_id=forecast.source_account_id,
        destination_account_id=forecast.destination_account_id,
        tags=tags,
        checkNumber=forecast.checkNumber,
    )

    # Hold the account ids before the delete, then create and delete together so
    # a failure can never leave the forecast row gone without its transaction.
    account_ids = {forecast.source_account_id, forecast.destination_account_id}
    with db_transaction.atomic():
        create_transactions([new_transaction])
        ForecastCacheTransaction.objects.filter(
            Q(id=forecast_id)
        ).delete()

    for account_id in account_ids:
        if account_id:
            delete_pattern(account_all(account_id))
    broadcast_invalidate(
        ["accounts", "account_forecast", "tag_graph", "transactions"]
    )
