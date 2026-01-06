from ninja import Router, Query
from ninja.errors import HttpError
from transactions.models import Transaction, Paycheck, TransactionDetail
from administration.models import DescriptionHistory
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
from tags.api.dependencies.custom_tag import CustomTag
from transactions.api.dependencies.full_transaction import FullTransaction
from transactions.api.dependencies.create_transactions import (
    create_transactions,
)
import traceback
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
        transaction = None
        paycheck_id = None
        transactions_to_create = []
        tags = []
        # Update Description History
        try:
            existing_description = DescriptionHistory.objects.get(
                description_normalized=payload.description.lower()
            )
            if payload.details:
                existing_description.tag_id = payload.details[0].tag_id
            else:
                existing_description.tag_id = None
            existing_description.save()
        except DescriptionHistory.DoesNotExist:
            tag_id = None
            if payload.details:
                tag_id = payload.details[0].tag_id
            DescriptionHistory.objects.create(
                description_normalized=payload.description.lower(),
                description_pretty=payload.description,
                tag_id=tag_id,
            )

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
                    tag_full_toggle=detail.tag_full_toggle,
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
            api_logger.info("Transaction created")

            return {"id": None}
        else:
            raise Exception("Error creating transaction")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Transaction not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record creation error : {str(e)}")
        traceback.print_exc()


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
            pattern = f"*account_{account}_transactions*"
            delete_pattern(pattern)
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
        # Fetch all relevant transactions at once
        transactions = Transaction.objects.filter(id__in=payload.transactions)
        transactions.delete()
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
        # Setup variables
        today = get_todays_date_timezone_adjusted()
        paycheck = None

        # Get the transaction to update
        transaction = get_object_or_404(Transaction, id=transaction_id)

        # Update Description History
        try:
            existing_description = DescriptionHistory.objects.get(
                description_normalized=payload.description.lower()
            )
            if payload.details:
                existing_description.tag_id = payload.details[0].tag_id
            else:
                existing_description.tag_id = None
            existing_description.save()
        except DescriptionHistory.DoesNotExist:
            tag_id = None
            if payload.details:
                tag_id = payload.details[0].tag_id
            DescriptionHistory.objects.create(
                description_normalized=payload.description.lower(),
                description_pretty=payload.description,
                tag_id=tag_id,
            )

        # Get Details
        existing_details = TransactionDetail.objects.filter(
            transaction_id=transaction_id
        )
        existing_details.delete()
        for detail in payload.details:
            adj_amount = 0
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
        api_logger.info("Paycheck deleted")

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
        api_logger.info(f"Transaction updated : {transaction_id}")

        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
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
