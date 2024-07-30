from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from transactions.models import Transaction, Paycheck
from transactions.api.schemas.transaction import (
    TransactionIn,
    TransactionClear,
    TransactionOut,
)
from administration.api.dependencies.log_to_db import logToDB
from django.shortcuts import get_object_or_404
from typing import List
from django.db.models import (
    Case,
    When,
    Q,
    IntegerField,
    Value,
    F,
    CharField,
    Sum,
    Subquery,
    OuterRef,
    FloatField,
    Window,
    ExpressionWrapper,
    DecimalField,
    Func,
    Count,
)
from django.db.models.functions import Concat, Coalesce, Abs
from typing import List, Optional, Dict, Any
from tags.api.dependencies.custom_tag import CustomTag
from transactions.api.dependencies.full_transaction import FullTransaction
from transactions.api.dependencies.create_transactions import (
    create_transactions,
)
import traceback

transaction_router = Router(tags=["Transactions"])


@transaction_router.post("/create")
def create_transaction(request, payload: TransactionIn):
    """
    The function `create_transaction` creates a transaction

    Args:
        request ():
        payload (TransactionIn): An object using schema of TransactionIn.

    Returns:
        id: returns the id of the created transaction
    """

    try:
        transaction = None
        paycheck_id = None
        transactions_to_create = []
        tags = []
        # Create paycheck
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
        if payload.details is not None:
            for detail in payload.details:
                tag_obj = CustomTag(
                    tag_name=detail.tag_pretty_name,
                    tag_amount=detail.tag_amt,
                    tag_id=detail.tag_id,
                )
                tags.append(tag_obj)
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
        transactions_to_create.append(transaction)
        if create_transactions(transactions_to_create):
            logToDB(
                "Transaction created",
                None,
                None,
                None,
                3001005,
                1,
            )

            return {"id": None}
        else:
            raise Exception("Error creating transaction")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, f"Record creation error : {str(e)}")
        traceback.print_exc()


@transaction_router.patch("/clear/{transaction_id}")
def clear_transaction(request, transaction_id: int, payload: TransactionClear):
    """
    The function `clear_transaction` changes the status to cleared, edit date to today
    of the transaction specified by id.  Skips transactions with a related Reminder.

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_id (int): the id of the transaction to update
        payload (TransactionClear): a transaction clear object

    Returns:
        success: True

    Raises:
        Http404: If the transaction with the specified ID does not exist.
    """

    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction.status_id = payload.status_id
        transaction.edit_date = payload.edit_date
        transaction.save()
        logToDB(
            f"Transaction cleared : #{transaction_id}",
            None,
            None,
            transaction_id,
            3002005,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not cleared : {str(e)}",
            None,
            None,
            transaction_id,
            3002905,
            2,
        )
        raise HttpError(500, "Transaction clear error")


@transaction_router.get("/get/{transaction_id}", response=TransactionOut)
def get_transaction(request, transaction_id: int):
    """
    The function `get_transaction` retrieves the transaction by id

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_id (int): The id of the transaction to retrieve.

    Returns:
        TransactionOut: the transaction object

    Raises:
        Http404: If the transaction with the specified ID does not exist.
    """

    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        logToDB(
            f"Transaction retrieved : #{transaction.id}",
            None,
            None,
            transaction.id,
            3001006,
            1,
        )
        return transaction
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@transaction_router.delete("/delete/{transaction_id}")
def delete_transaction(request, transaction_id: int):
    """
    The function `delete_transaction` deletes the transaction specified by id,
    but skips any that have a related reminder.

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_id (int): the id of the transaction to delete

    Returns:
        success: True

    Raises:
        Http404: If the transaction with the specified ID does not exist.
    """

    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        transaction.delete()
        logToDB(
            f"Transaction deleted : #{transaction_id}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@transaction_router.put("/update/{transaction_id}")
def update_transaction(request, transaction_id: int, payload: TransactionIn):
    """
    The function `update_transaction` updates the transaction specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        transaction_id (int): the id of the transaction to update
        payload (TransactionIn): a transaction object

    Returns:
        success: True

    Raises:
        Http404: If the transaction with the specified ID does not exist.
    """

    try:
        # Setup variables
        today = get_todays_date_timezone_adjusted()
        paycheck = None

        # Get the transaction to update
        transaction = get_object_or_404(Transaction, id=transaction_id)

        # Get Details
        existing_details = TransactionDetail.objects.filter(
            transaction_id=transaction_id
        )
        existing_details.delete()
        for detail in payload.details:
            adj_amount = 0
            if payload.transaction_type_id == 1:
                adj_amount = -abs(detail.tag_amt)
            else:
                adj_amount = abs(detail.tag_amt)
            TransactionDetail.objects.create(
                transaction_id=transaction_id,
                detail_amt=adj_amount,
                tag_id=detail.tag_id,
            )
            logToDB(
                "Transaction detail created",
                None,
                None,
                transaction_id,
                3001001,
                1,
            )

        # Get existing paycheck if it exists
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
            logToDB(
                "Paycheck updated",
                None,
                None,
                transaction_id,
                3001002,
                1,
            )

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
            logToDB(
                "Paycheck created",
                None,
                None,
                transaction_id,
                3001001,
                1,
            )

        # Delete existing paycheck if no paycheck info passed
        if payload.paycheck is None and paycheck is not None:
            paycheck.delete()
        logToDB(
            "Paycheck deleted",
            None,
            None,
            transaction_id,
            3001003,
            1,
        )

        # Update the transaction
        transaction.transaction_date = payload.transaction_date
        transaction.total_amount = payload.total_amount
        transaction.status_id = payload.status_id
        transaction.memo = payload.memo
        transaction.description = payload.description
        transaction.edit_date = today
        transaction.source_account_id = payload.source_account_id
        transaction.destination_account_id = payload.destination_account_id
        transaction.checkNumber = payload.checkNumber
        if paycheck is not None:
            transaction.paycheck_id = paycheck.id
        else:
            transaction.paycheck_id = None
        transaction.save()
        logToDB(
            f"Transaction updated : {transaction_id}",
            None,
            None,
            transaction_id,
            3001002,
            1,
        )

        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Transaction not updated : {str(e)}",
            None,
            None,
            transaction_id,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")
