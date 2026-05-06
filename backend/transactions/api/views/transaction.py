from ninja import Router, Query
from ninja.errors import HttpError
from transactions.models import Transaction, TransactionDetail
from accounts.models import Account
from transactions.api.schemas.transaction import (
    TransactionIn,
    TransactionList,
    TransactionOut,
    PaginatedTransactions,
    MultiTranscationDate,
    TransactionQuery,
)
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.db.models import (
    Case,
    When,
    Value,
    F,
    CharField,
    Subquery,
    OuterRef,
    DecimalField,
)
from django.db.models.functions import Concat, Coalesce, Abs
from transactions.services.transaction import (
    create_transaction_service,
    update_transaction_service,
)
from utils.dates import (
    get_todays_date_timezone_adjusted,
)
from transactions.api.dependencies.sort_transactions import sort_transactions
from datetime import timedelta
from django.core.paginator import Paginator
from transactions.api.dependencies.get_transactions_by_account import (
    get_transactions_by_account,
)
from backend.utils.cache import delete_pattern
from core.cache.keys import (
    account_pending_balance,
    account_cleared_balance,
    account_financials,
)
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

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
        create_transaction_service(payload)
        for account_id in filter(None, [payload.source_account_id, payload.destination_account_id]):
            delete_pattern(f"*account:{account_id}:transactions*")
            delete_pattern(account_pending_balance(account_id))
            delete_pattern(account_cleared_balance(account_id))
            delete_pattern(account_financials(account_id))
        return {"id": None}
    except Exception as e:
        api_logger.error("Transaction not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record creation error : {str(e)}")


@transaction_router.patch("/multiedit")
def multiedit_transactions(request, payload: MultiTranscationDate):
    """
    The function `multiedit_transactions` changes the transaction dates of mutliple
    transactions.

    Args:
        request (HttpRequest): The HTTP request object.
        payload (MultiTransactionDate): A list of transactions and date to change.

    Returns:
        dict: A dictionary with the key 'success' and value True.

    Raises:
        HttpError: Raises an HTTP error if there's an exception during processing.
    """
    try:
        edit_date = get_todays_date_timezone_adjusted()
        # Fetch all relevant transactions at once
        transactions = Transaction.objects.filter(
            id__in=payload.transaction_ids
        )

        # Make changes
        transactions.update(
            transaction_date=payload.new_date, edit_date=edit_date
        )

        api_logger.info(
            f"Transaction dates updated: #{payload.transaction_ids}"
        )

        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Tranasction dates not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Transaction dates error: {str(e)}")


@transaction_router.patch("/clear")
def clear_transaction(request, payload: TransactionList):
    """
    The function `clear_transaction` changes the status to cleared, edits the date to today
    of the transaction(s) specified by id. Skips transactions with a related Reminder.

    Args:
        request (HttpRequest): The HTTP request object.
        payload (TransactionList): A list of transaction ids to clear.

    Returns:
        dict: A dictionary with the key 'success' and value True.

    Raises:
        HttpError: Raises an HTTP error if there's an exception during processing.
    """
    try:
        # Fetch all relevant transactions at once
        transactions = Transaction.objects.filter(id__in=payload.transactions)

        # Prepare a list to hold transactions that need to be updated
        transactions_to_update = []
        accounts_effected = []

        for transaction in transactions:
            accounts_effected.append(transaction.source_account.id)
            if transaction.destination_account:
                accounts_effected.append(transaction.destination_account.id)
            if transaction.status_id == 2:
                transaction.status_id = 1
            elif transaction.status_id == 1:
                transaction.status_id = 2

            transaction.edit_date = get_todays_date_timezone_adjusted()
            transactions_to_update.append(transaction)

            # Log the transaction
            api_logger.info(f"Transaction cleared: #{transaction.id}")

        # Perform a bulk update on the modified transactions
        if transactions_to_update:
            Transaction.objects.bulk_update(
                transactions_to_update, ["status_id", "edit_date"]
            )
        unique_accounts = list(set(accounts_effected))
        for account in unique_accounts:
            delete_pattern(f"*account:{account}:transactions*")
            delete_pattern(account_pending_balance(account))
            delete_pattern(account_cleared_balance(account))
            delete_pattern(account_financials(account))
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction clear error")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Transaction clear error: {str(e)}")


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
        api_logger.debug(f"Transaction retrieved : #{transaction.id}")
        return transaction
    except Http404:
        raise HttpError(404, "Transaction not found")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, "Record retrieval error")


@transaction_router.patch("/delete")
def delete_transaction(request, payload: TransactionList):
    """
    The function `delete_transaction` deletes the transaction(s) specified by id,
    but skips any that have a related reminder.

    Args:
        request (HttpRequest): The HTTP request object.
        payload (TransactionList): list of transaction ids to delete

    Returns:
        success: True

    Raises:
    """

    try:
        transactions = Transaction.objects.filter(id__in=payload.transactions)
        account_ids = set()
        for t in transactions:
            account_ids.add(t.source_account_id)
            if t.destination_account_id:
                account_ids.add(t.destination_account_id)
        transactions.delete()
        for account_id in account_ids:
            delete_pattern(f"*account:{account_id}:transactions*")
            delete_pattern(account_pending_balance(account_id))
            delete_pattern(account_cleared_balance(account_id))
            delete_pattern(account_financials(account_id))
        for transaction in payload.transactions:
            api_logger.info(f"Transaction deleted : #{transaction}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction not deleted")
        error_logger.error(f"{str(e)}")
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
        existing = get_object_or_404(Transaction, id=transaction_id)
        old_source_id = existing.source_account_id
        old_destination_id = existing.destination_account_id

        update_transaction_service(transaction_id, payload)

        # If the account changed, the post_save signal only busts the new
        # account's cache — manually bust the old account(s) too.
        old_ids = {old_source_id, old_destination_id} - {None}
        new_ids = {payload.source_account_id, payload.destination_account_id} - {None}
        for account_id in old_ids - new_ids:
            delete_pattern(account_pending_balance(account_id))
            delete_pattern(account_cleared_balance(account_id))
            delete_pattern(account_financials(account_id))
            delete_pattern(f"*account:{account_id}:transactions*")

        return {"success": True}
    except Http404:
        raise HttpError(404, "Transaction not found")
    except Exception as e:
        api_logger.error("Transaction not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record update error: {str(e)}")


@transaction_router.get("/list", response=PaginatedTransactions)
def list_transactions(request, query: TransactionQuery = Query(...)):
    """
    The function `list_transactions` retrieves a list of transactions,
    ordered by status, transaction date ascending, custom transaction type,
    and total_amount.
    If this is for a forecast, you can specify the maximum days in the future
    to display transactions from.  If this is not for a forecast, you can specify the
    maxmimum days in the past to view transactions from.  If an account is specified,
    transactions are filtered by that account.  Defaults are no account, 14 days in the past
    and not a forecast.

    Args:
        request (HttpRequest): The HTTP request object.
        account (int): Optional account to filter transactions by.
        maxdays (int): Optional days in the past if not a forecast, days in the future
            if a forecast, default is 14.
        forecast (bool): Optional boolean wether this request is a forecast or not.

    Returns:
        TransactionOut: a list of transaction objects
    """

    try:

        # If view_type is 1, filter transactions for maximum days and transaction
        # details that match account
        if query.view_type == 1:
            # Set end_date
            end_date = get_todays_date_timezone_adjusted() + timedelta(
                days=query.maxdays
            )

            # Get a complete list of transactions, including reminders, sorted with totals
            all_transactions_list, previous_balance = (
                get_transactions_by_account(
                    end_date, query.account, False, query.forecast
                )
            )

            # Reverse transactions if not forecast
            if not query.forecast:
                reversed_all_transactions_list = list(
                    reversed(all_transactions_list)
                )

            # Paginate transactions
            total_pages = 0
            if query.page_size is not None and query.page is not None:
                paginator = None
                if not query.forecast:
                    paginator = Paginator(
                        reversed_all_transactions_list, query.page_size
                    )
                else:
                    paginator = Paginator(
                        all_transactions_list, query.page_size
                    )
                page_obj = paginator.page(query.page)
                qs = list(page_obj.object_list)
                total_pages = paginator.num_pages
            else:
                qs = all_transactions_list
            total_records = len(all_transactions_list)
            paginated_obj = PaginatedTransactions(
                transactions=qs,
                current_page=query.page,
                total_pages=total_pages,
                total_records=total_records,
            )
            return paginated_obj

        # If view_type is not 1
        else:

            # Initialize queryset
            qs = None

            # Setup subqueries
            source_account_name = Account.objects.filter(
                id=OuterRef("source_account_id")
            ).values("account_name")[:1]
            destination_account_name = Account.objects.filter(
                id=OuterRef("destination_account_id")
            ).values("account_name")[:1]

            # If this is upcoming transaction
            # Filter transactions for pending status
            if query.view_type == 2:
                qs = Transaction.objects.filter(status_id=1)
            # If this is rule transactions
            # Filter by tag and maxdays
            elif query.view_type == 3:
                end_date = get_todays_date_timezone_adjusted()
                start_date = get_todays_date_timezone_adjusted() - timedelta(
                    days=query.maxdays
                )
                qs = Transaction.objects.filter(
                    add_date__range=(start_date, end_date)
                )

            # Set order of transactions
            qs = sort_transactions(qs)
            # Return only 10 records for upcoming transactions
            if query.view_type == 2:
                qs = qs[:10]
            qs = qs.annotate(
                source_name=Coalesce(
                    Subquery(source_account_name),
                    Value("Unknown Account"),
                ),
                destination_name=Coalesce(
                    Subquery(destination_account_name),
                    Value("Unknown Account"),
                ),
            )
            qs = qs.annotate(
                pretty_account=Case(
                    When(
                        transaction_type_id=3,
                        then=Concat(
                            F("source_name"),
                            Value(" => "),
                            F("destination_name"),
                        ),
                    ),
                    default=F("source_name"),
                    output_field=CharField(),  # Correctly specify the output field
                )
            )
            qs = qs.annotate(
                pretty_total=Case(
                    When(
                        transaction_type_id=2,
                        then=Abs(F("total_amount")),
                    ),
                    When(
                        transaction_type_id=1,
                        then=-Abs(F("total_amount")),
                    ),
                    When(
                        transaction_type_id=3,
                        then=-Abs(F("total_amount")),
                    ),
                    default=Value(
                        0,
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    ),  # Ensure the correct output field
                    output_field=DecimalField(
                        max_digits=12, decimal_places=2
                    ),  # Ensure the correct output field
                )
            )

            # Add tags
            for transaction in qs:
                transaction_details = TransactionDetail.objects.filter(
                    transaction_id=transaction.id
                )
                details = list(transaction_details)
                tags = list(
                    transaction_details.annotate(
                        parent_tag=F("tag__parent__tag_name"),
                        child_tag=F("tag__child__tag_name"),
                        tag_name_combined=Case(
                            When(child_tag__isnull=True, then=F("parent_tag")),
                            default=Concat(
                                F("parent_tag"), Value(" / "), F("child_tag")
                            ),
                            output_field=CharField(),
                        ),
                    )
                    .exclude(tag_name_combined__isnull=True)
                    .values_list("tag_name_combined", flat=True)
                )
                transaction.tags = tags
                transaction.details = details
            query = list(qs)
            paginated_obj = PaginatedTransactions(
                transactions=query,
                current_page=1,
                total_pages=1,
                total_records=len(query),
            )
            return paginated_obj
        api_logger.debug("Transaction list retrieved")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction list not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")
