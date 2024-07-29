from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from transactions.models import Transaction, Paycheck
from transactions.api.schemas.transaction import TransactionIn
from administration.models import logToDB
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
