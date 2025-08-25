from typing import List
from transactions.api.dependencies.full_transaction import FullTransaction
from transactions.models import Transaction, TransactionDetail
from django.db import transaction
from administration.api.dependencies.log_to_db import logToDB


def create_transactions(transactions: List[FullTransaction]):
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
                                    TransactionDetail.objects.create(
                                        transaction_id=created_transaction.id,
                                        detail_amt=adj_amount,
                                        tag_id=tag.tag_id,
                                        full_toggle=tag.tag_full_toggle,
                                    )
                        except Exception as e:
                            logToDB(
                                f"Transaction detail creation error: {e}",
                                None,
                                None,
                                None,
                                3001901,
                                2,
                            )
                    except Exception as e:
                        logToDB(
                            f"Transaction creation error: {e}",
                            None,
                            None,
                            None,
                            3001901,
                            2,
                        )
                logToDB(
                    "Transaction(s) created successfully",
                    None,
                    None,
                    None,
                    3001001,
                    1,
                )
                return True
            except Exception as e:
                print(f"Unable to create transaction(s): {e}")
                transaction.rollback()
                logToDB(
                    f"Transaction(s) not created: {e}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
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
                for step, chunk in enumerate(chunks, start=0):
                    created_transactions.extend(
                        Transaction.objects.bulk_create(chunk)
                    )
                logToDB(
                    "Transaction chunks created successfully",
                    None,
                    None,
                    None,
                    3001001,
                    1,
                )
            except Exception as e:
                logToDB(
                    f"Transaction chunks not created: {e}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
            # Create transaction details
            for trans_detail in transaction_details:
                transaction_index = trans_detail["transaction_index"]
                detail_amt = trans_detail["detail_amt"]
                tag_id = trans_detail["tag_id"]
                full_toggle = trans_detail["full_toggle"]
                print(
                    f"index: {transaction_index}, amt: {detail_amt}, tag_id:{tag_id}"
                )
                detail = TransactionDetail(
                    transaction_id=created_transactions[transaction_index].id,
                    detail_amt=detail_amt,
                    tag_id=tag_id,
                    full_toggle=full_toggle,
                )
                details_to_create.append(detail)
            try:
                chunks = list(chunk_list(details_to_create, max_bulk))
                for step, chunk in enumerate(chunks, start=0):
                    TransactionDetail.objects.bulk_create(chunk)
                logToDB(
                    "Transaction detail chunks created successfully",
                    None,
                    None,
                    None,
                    3001001,
                    1,
                )
            except Exception as e:
                logToDB(
                    f"Transaction detail chunks not created: {e}",
                    None,
                    None,
                    None,
                    3001901,
                    2,
                )
            logToDB(
                "Transaction(s) created successfully",
                None,
                None,
                None,
                3001001,
                1,
            )
            # update_running_totals()
            return True
        except Exception as e:
            logToDB(
                f"Transaction(s) not created: {e}",
                None,
                None,
                None,
                3001901,
                2,
            )
            return False
