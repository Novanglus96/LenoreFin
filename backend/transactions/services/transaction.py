from typing import Optional
from django.shortcuts import get_object_or_404
from administration.models import DescriptionHistory
from transactions.models import Transaction, Paycheck, TransactionDetail
from transactions.api.schemas.transaction import TransactionIn
from transactions.api.dependencies.full_transaction import FullTransaction
from transactions.api.dependencies.create_transactions import create_transactions
from tags.api.dependencies.custom_tag import CustomTag
from utils.dates import get_todays_date_timezone_adjusted
import logging

api_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")


def upsert_description_history(
    description: str, tag_id: Optional[int] = None
) -> None:
    """
    Create or update a DescriptionHistory record for the given description.

    Args:
        description (str): The transaction description.
        tag_id (Optional[int]): The tag id to associate, or None.
    """
    try:
        existing = DescriptionHistory.objects.get(
            description_normalized=description.lower()
        )
        existing.tag_id = tag_id
        existing.save()
    except DescriptionHistory.DoesNotExist:
        DescriptionHistory.objects.create(
            description_normalized=description.lower(),
            description_pretty=description,
            tag_id=tag_id,
        )


def create_transaction_service(payload: TransactionIn) -> None:
    """
    Create a new transaction from a TransactionIn payload.

    Args:
        payload (TransactionIn): The validated transaction input.

    Raises:
        Exception: If transaction creation fails.
    """
    paycheck_id = None
    tags = []

    # Determine tag_id from first detail (if any)
    tag_id = payload.details[0].tag_id if payload.details else None
    upsert_description_history(payload.description, tag_id)

    # Create paycheck if provided
    if payload.paycheck is not None:
        paycheck = Paycheck.objects.create(
            gross=payload.paycheck.gross,
            net=payload.paycheck.net,
            taxes=payload.paycheck.taxes,
            health=payload.paycheck.health,
            pension=payload.paycheck.pension,
            fsa=payload.paycheck.fsa,
            dca=payload.paycheck.dca,
            union_dues=payload.paycheck.union_dues,
            four_fifty_seven_b=payload.paycheck.four_fifty_seven_b,
            payee_id=payload.paycheck.payee_id,
        )
        paycheck_id = paycheck.id

    # Build CustomTag list from details
    if payload.details is not None:
        for detail in payload.details:
            tag_obj = CustomTag(
                tag_name=detail.tag_pretty_name,
                tag_amount=detail.tag_amt,
                tag_id=detail.tag_id,
                tag_full_toggle=detail.tag_full_toggle,
            )
            tags.append(tag_obj)

    # Build FullTransaction and create it
    transaction = FullTransaction(
        transaction_date=payload.transaction_date,
        total_amount=payload.total_amount,
        status_id=payload.status_id,
        memo=payload.memo,
        description=payload.description,
        edit_date=payload.edit_date,
        add_date=payload.add_date,
        transaction_type_id=payload.transaction_type_id,
        paycheck_id=paycheck_id,
        source_account_id=payload.source_account_id,
        destination_account_id=payload.destination_account_id,
        tags=tags,
        checkNumber=payload.checkNumber,
    )

    if not create_transactions([transaction]):
        raise Exception("Error creating transaction")

    api_logger.info("Transaction created")


def update_transaction_service(transaction_id: int, payload: TransactionIn) -> None:
    """
    Update an existing transaction by id.

    Args:
        transaction_id (int): The id of the transaction to update.
        payload (TransactionIn): The validated transaction input.

    Raises:
        Http404: If the transaction does not exist.
        Exception: If any other error occurs during update.
    """
    today = get_todays_date_timezone_adjusted()
    paycheck = None

    # Get the transaction — raises Http404 if not found
    transaction = get_object_or_404(Transaction, id=transaction_id)

    # Determine tag_id from first detail (if any)
    tag_id = payload.details[0].tag_id if payload.details else None
    upsert_description_history(payload.description, tag_id)

    # Delete existing details and recreate
    existing_details = TransactionDetail.objects.filter(
        transaction_id=transaction_id
    )
    existing_details.delete()
    for detail in (payload.details or []):
        if payload.transaction_type_id == 2:
            if not detail.tag_full_toggle:
                adj_amount = abs(detail.tag_amt)
            else:
                adj_amount = abs(payload.total_amount)
        else:
            if not detail.tag_full_toggle:
                adj_amount = -abs(detail.tag_amt)
            else:
                adj_amount = -abs(payload.total_amount)
        TransactionDetail.objects.create(
            transaction_id=transaction_id,
            detail_amt=adj_amount,
            tag_id=detail.tag_id,
            full_toggle=detail.tag_full_toggle,
        )
        api_logger.info("Transaction detail created")

    # Get existing paycheck if one is linked
    if transaction.paycheck_id is not None:
        paycheck = get_object_or_404(Paycheck, id=transaction.paycheck_id)

    # Update existing paycheck
    if payload.paycheck is not None and paycheck is not None:
        paycheck.gross = payload.paycheck.gross
        paycheck.net = payload.paycheck.net
        paycheck.taxes = payload.paycheck.taxes
        paycheck.health = payload.paycheck.health
        paycheck.pension = payload.paycheck.pension
        paycheck.fsa = payload.paycheck.fsa
        paycheck.dca = payload.paycheck.dca
        paycheck.union_dues = payload.paycheck.union_dues
        paycheck.four_fifty_seven_b = payload.paycheck.four_fifty_seven_b
        paycheck.payee_id = payload.paycheck.payee_id
        paycheck.save()
        api_logger.info("Paycheck updated")

    # Create new paycheck
    if payload.paycheck is not None and paycheck is None:
        paycheck = Paycheck.objects.create(
            gross=payload.paycheck.gross,
            net=payload.paycheck.net,
            taxes=payload.paycheck.taxes,
            health=payload.paycheck.health,
            pension=payload.paycheck.pension,
            fsa=payload.paycheck.fsa,
            dca=payload.paycheck.dca,
            union_dues=payload.paycheck.union_dues,
            four_fifty_seven_b=payload.paycheck.four_fifty_seven_b,
            payee_id=payload.paycheck.payee_id,
        )
        api_logger.info("Paycheck created")

    # Delete existing paycheck if no paycheck info passed
    if payload.paycheck is None and paycheck is not None:
        paycheck.delete()
        paycheck = None
    api_logger.info("Paycheck deleted")

    # Update the transaction fields
    transaction.transaction_date = payload.transaction_date
    transaction.total_amount = payload.total_amount
    transaction.status_id = payload.status_id
    transaction.memo = payload.memo
    transaction.description = payload.description
    transaction.edit_date = today
    transaction.source_account_id = payload.source_account_id
    transaction.destination_account_id = payload.destination_account_id
    transaction.checkNumber = payload.checkNumber
    transaction.paycheck_id = paycheck.id if paycheck is not None else None
    transaction.save()

    api_logger.info(f"Transaction updated : {transaction_id}")
