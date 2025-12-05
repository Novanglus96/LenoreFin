from typing import List
from transactions.api.dependencies.full_transaction import FullTransaction
from transactions.models import (
    Transaction,
    TransactionDetail,
    ReminderCacheTransaction,
    ReminderCacheTransactionDetail,
    ForecastCacheTransaction,
    ForecastCacheTransactionDetail,
)
from django.db import transaction
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


def create_transactions(
    transactions: List[FullTransaction], transaction_type: str = "transaction"
):
    """
    The function `create_transactions` creates transactions either individually
    or using bulk_create based on paramters.

    Args:
        transactions (List[FullTransaction]): a list of at least 1 transaction to create
    Returns:
        bool: Returns true or false depending on success
    """

    # Initiate variables...
    max_bulk = 1000  # Chunk size for bulk record creations
    bulk_lower_limit = 10  # Lower limit to process as bulk_create

    # Define how to break up records into chunks
    def chunk_list(lst, chunk_size):
        for i in range(0, len(lst), chunk_size):
            yield lst[i : i + chunk_size]

    # Determine wether to process as individual creations or use bulk_create
    if len(transactions) <= bulk_lower_limit:
        with transaction.atomic():
            try:
                for trans in transactions:
                    try:
                        if trans.transaction_type_id == 1:
                            amount = -abs(trans.total_amount)
                        elif trans.transaction_type_id == 2:
                            amount = abs(trans.total_amount)
                        elif trans.transaction_type_id == 3:
                            amount = -abs(trans.total_amount)
                        created_transaction = None
                        if transaction_type == "transaction":
                            created_transaction = Transaction.objects.create(
                                transaction_date=trans.transaction_date,
                                total_amount=amount,
                                status_id=trans.status_id,
                                memo=trans.memo,
                                description=trans.description,
                                edit_date=trans.edit_date,
                                add_date=trans.add_date,
                                transaction_type_id=trans.transaction_type_id,
                                paycheck_id=trans.paycheck_id,
                                source_account_id=trans.source_account_id,
                                destination_account_id=trans.destination_account_id,
                                checkNumber=trans.checkNumber,
                            )
                        if transaction_type == "reminder":
                            created_transaction = ReminderCacheTransaction.objects.create(
                                transaction_date=trans.transaction_date,
                                total_amount=amount,
                                status_id=trans.status_id,
                                memo=trans.memo,
                                description=trans.description,
                                edit_date=trans.edit_date,
                                add_date=trans.add_date,
                                transaction_type_id=trans.transaction_type_id,
                                paycheck_id=trans.paycheck_id,
                                source_account_id=trans.source_account_id,
                                destination_account_id=trans.destination_account_id,
                                checkNumber=trans.checkNumber,
                                reminder_id=trans.reminder_id,
                            )
                        if transaction_type == "forecast":
                            created_transaction = ForecastCacheTransaction.objects.create(
                                transaction_date=trans.transaction_date,
                                total_amount=amount,
                                status_id=trans.status_id,
                                memo=trans.memo,
                                description=trans.description,
                                edit_date=trans.edit_date,
                                add_date=trans.add_date,
                                transaction_type_id=trans.transaction_type_id,
                                paycheck_id=trans.paycheck_id,
                                source_account_id=trans.source_account_id,
                                destination_account_id=trans.destination_account_id,
                                checkNumber=trans.checkNumber,
                            )
                        try:
                            if trans.tags and len(trans.tags) != 0:
                                for tag in trans.tags:
                                    adj_amount = 0
                                    if trans.transaction_type_id == 2:
                                        if not tag.tag_full_toggle:
                                            adj_amount = abs(tag.tag_amount)
                                        else:
                                            adj_amount = abs(trans.total_amount)
                                    else:
                                        if not tag.tag_full_toggle:
                                            adj_amount = -abs(tag.tag_amount)
                                        else:
                                            adj_amount = -abs(
                                                trans.total_amount
                                            )
                                    if transaction_type == "transaction":
                                        TransactionDetail.objects.create(
                                            transaction_id=created_transaction.id,
                                            detail_amt=adj_amount,
                                            tag_id=tag.tag_id,
                                            full_toggle=tag.tag_full_toggle,
                                        )
                                    if transaction_type == "reminder":
                                        ReminderCacheTransactionDetail.objects.create(
                                            transaction_id=created_transaction.id,
                                            detail_amt=adj_amount,
                                            tag_id=tag.tag_id,
                                            full_toggle=tag.tag_full_toggle,
                                        )
                                    if transaction_type == "forecast":
                                        ForecastCacheTransactionDetail.objects.create(
                                            transaction_id=created_transaction.id,
                                            detail_amt=adj_amount,
                                            tag_id=tag.tag_id,
                                            full_toggle=tag.tag_full_toggle,
                                        )
                        except Exception as e:
                            api_logger.error(
                                "Transaction detail creation error"
                            )
                            error_logger.error(f"{str(e)}")
                    except Exception as e:
                        api_logger.error("Transaction creation error")
                        error_logger.error(f"{str(e)}")
                api_logger.debug("Transaction(s) created successfully")
                return True
            except Exception as e:
                transaction.rollback()
                api_logger.warning("Transaction(s) not created")
                error_logger.warning(f"{str(e)}")
                return False
    else:
        try:
            transactions_to_create = []
            transaction_details = []
            details_to_create = []
            created_transactions = []
            for index, trans in enumerate(transactions):
                if trans.transaction_type_id == 1:
                    amount = -abs(trans.total_amount)
                elif trans.transaction_type_id == 2:
                    amount = abs(trans.total_amount)
                elif trans.transaction_type_id == 3:
                    amount = -abs(trans.total_amount)
                trans_obj = None
                if transaction_type == "transaction":
                    trans_obj = Transaction(
                        transaction_date=trans.transaction_date,
                        total_amount=amount,
                        status_id=trans.status_id,
                        memo=trans.memo,
                        description=trans.description,
                        edit_date=trans.edit_date,
                        add_date=trans.add_date,
                        transaction_type_id=trans.transaction_type_id,
                        paycheck_id=trans.paycheck_id,
                        source_account_id=trans.source_account_id,
                        destination_account_id=trans.destination_account_id,
                        checkNumber=trans.checkNumber,
                    )
                if transaction_type == "reminder":
                    trans_obj = ReminderCacheTransaction(
                        transaction_date=trans.transaction_date,
                        total_amount=amount,
                        status_id=trans.status_id,
                        memo=trans.memo,
                        description=trans.description,
                        edit_date=trans.edit_date,
                        add_date=trans.add_date,
                        transaction_type_id=trans.transaction_type_id,
                        paycheck_id=trans.paycheck_id,
                        source_account_id=trans.source_account_id,
                        destination_account_id=trans.destination_account_id,
                        checkNumber=trans.checkNumber,
                        reminder_id=trans.reminder_id,
                    )
                if transaction_type == "forecast":
                    trans_obj = ForecastCacheTransaction(
                        transaction_date=trans.transaction_date,
                        total_amount=amount,
                        status_id=trans.status_id,
                        memo=trans.memo,
                        description=trans.description,
                        edit_date=trans.edit_date,
                        add_date=trans.add_date,
                        transaction_type_id=trans.transaction_type_id,
                        paycheck_id=trans.paycheck_id,
                        source_account_id=trans.source_account_id,
                        destination_account_id=trans.destination_account_id,
                        checkNumber=trans.checkNumber,
                    )
                transactions_to_create.append(trans_obj)
                if trans.tags and len(trans.tags) != 0:
                    for tag in trans.tags:
                        adj_amount = 0
                        if trans.transaction_type_id == 2:
                            if not tag.tag_full_toggle:
                                adj_amount = abs(tag.tag_amount)
                            else:
                                adj_amount = abs(trans.total_amount)
                        else:
                            if not tag.tag_full_toggle:
                                adj_amount = -abs(tag.tag_amount)
                            else:
                                adj_amount = -abs(trans.total_amount)
                        detail_dict = {
                            "transaction_index": index,
                            "detail_amt": adj_amount,
                            "tag_id": tag.tag_id,
                            "full_toggle": tag.tag_full_toggle,
                        }
                        transaction_details.append(detail_dict)
            # Create transactions
            try:
                chunks = list(chunk_list(transactions_to_create, max_bulk))
                if transaction_type == "transaction":
                    for step, chunk in enumerate(chunks, start=0):
                        created_transactions.extend(
                            Transaction.objects.bulk_create(chunk)
                        )
                if transaction_type == "reminder":
                    for step, chunk in enumerate(chunks, start=0):
                        created_transactions.extend(
                            ReminderCacheTransaction.objects.bulk_create(chunk)
                        )
                if transaction_type == "forecast":
                    for step, chunk in enumerate(chunks, start=0):
                        created_transactions.extend(
                            ForecastCacheTransaction.objects.bulk_create(chunk)
                        )
                api_logger.info("Transaction chunks created successfully")
            except Exception as e:
                api_logger.error("Transaction chunks not created")
                error_logger.error(f"{str(e)}")
            # Create transaction details
            for trans_detail in transaction_details:
                transaction_index = trans_detail["transaction_index"]
                detail_amt = trans_detail["detail_amt"]
                tag_id = trans_detail["tag_id"]
                full_toggle = trans_detail["full_toggle"]
                detail = None
                if transaction_type == "transactions":
                    detail = TransactionDetail(
                        transaction_id=created_transactions[
                            transaction_index
                        ].id,
                        detail_amt=detail_amt,
                        tag_id=tag_id,
                        full_toggle=full_toggle,
                    )
                if transaction_type == "reminder":
                    detail = ReminderCacheTransactionDetail(
                        transaction_id=created_transactions[
                            transaction_index
                        ].id,
                        detail_amt=detail_amt,
                        tag_id=tag_id,
                        full_toggle=full_toggle,
                    )
                if transaction_type == "forecast":
                    detail = ForecastCacheTransactionDetail(
                        transaction_id=created_transactions[
                            transaction_index
                        ].id,
                        detail_amt=detail_amt,
                        tag_id=tag_id,
                        full_toggle=full_toggle,
                    )
                details_to_create.append(detail)
            try:
                chunks = list(chunk_list(details_to_create, max_bulk))
                if transaction_type == "transaction":
                    for step, chunk in enumerate(chunks, start=0):
                        TransactionDetail.objects.bulk_create(chunk)
                if transaction_type == "reminder":
                    for step, chunk in enumerate(chunks, start=0):
                        ReminderCacheTransactionDetail.objects.bulk_create(
                            chunk
                        )
                if transaction_type == "forecast":
                    for step, chunk in enumerate(chunks, start=0):
                        ForecastCacheTransactionDetail.objects.bulk_create(
                            chunk
                        )
                api_logger.info(
                    "Transaction detail chunks created successfully"
                )
            except Exception as e:
                api_logger.error("Transaction detail chunks not created")
                error_logger.error(f"{str(e)}")
            api_logger.info("Transaction(s) created successfully")
            # update_running_totals()
            return True
        except Exception as e:
            api_logger.error("Transaction(s) not created")
            error_logger.error(f"{str(e)}")
            return False
