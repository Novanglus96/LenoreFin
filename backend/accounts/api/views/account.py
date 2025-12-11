from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from accounts.models import Account, Reward
from transactions.models import Transaction
from accounts.api.schemas.account import (
    AccountIn,
    AccountOut,
    AccountUpdate,
    AccountQuery,
)
from django.shortcuts import get_object_or_404
from typing import List
from django.db.models import (
    Case,
    When,
    Value,
    F,
    Sum,
    Subquery,
    OuterRef,
    ExpressionWrapper,
    DecimalField,
    Q,
    Max,
)
from django.db.models.functions import Coalesce, Abs, TruncMonth
from administration.api.dependencies.apply_patch import apply_patch
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
from dateutil.relativedelta import relativedelta
from datetime import timedelta
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


account_router = Router(tags=["Accounts"])


@account_router.post("/create")
def create_account(request, payload: AccountIn):
    """
    The function `create_account` creates an account

    Args:
        request ():
        payload (AccountIn): An object using schema of AccountIn.

    Returns:
        id: returns the id of the created account
    """

    try:
        account = Account.objects.create(**payload.dict())
        api_logger.info(f"Account created : {account.account_name}")
        return {"id": account.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Account not created : name exists ({payload.account_name})"
            )
            error_logger.error(
                f"Account not created : name exists ({payload.account_name})"
            )
            raise HttpError(400, "Account name already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Account not created : db integrity error")
            error_logger.error("Account not created : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Account not created")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record creation error: {str(e)}")


@account_router.get("/get/{account_id}", response=AccountOut)
def get_account(request, account_id: int):
    """
    The function `get_account` retrieves the account by id

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): The id of the account to retrieve.

    Returns:
        AccountOut: the account object

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:

        # Retrieve the account object from the database
        qs = Account.objects.filter(id=account_id)

        # Set variables
        today = get_todays_date_timezone_adjusted()
        due_day = qs.first().due_day
        statement_day = qs.first().statement_day
        statement_date = today
        due_date = today

        # Calculate Next Statement Date / Due Date
        if due_day > today.day:
            due_date = today.replace(day=1) + relativedelta(day=due_day)
        else:
            due_date = today.replace(day=1) + relativedelta(
                months=1, day=due_day
            )

        if statement_day > today.day:
            statement_date = today.replace(day=1) + relativedelta(
                day=statement_day
            )
        else:
            statement_date = today.replace(day=1) + relativedelta(
                months=1, day=statement_day
            )

        # Subquery to get the latest rewards amount
        rewards_total_amount = 0
        rewards_total_object = (
            Reward.objects.filter(reward_account_id=account_id)
            .order_by("-reward_date", "-id")
            .first()
        )
        if rewards_total_object:
            rewards_total_amount = rewards_total_object.reward_amount

        # Subquery to calculate sum of pretty_total grouped by source_account_id
        source_balance_subquery = (
            Transaction.objects.filter(
                source_account_id=OuterRef("pk"),
                status_id__in=[2, 3],  # Adjust status conditions as needed
            )
            .annotate(
                pretty_total=Case(
                    When(transaction_type_id=2, then=Abs(F("total_amount"))),
                    When(transaction_type_id=1, then=-Abs(F("total_amount"))),
                    When(
                        transaction_type_id=3,
                        then=Case(
                            When(
                                source_account_id=OuterRef("pk"),
                                then=-Abs(F("total_amount")),
                            ),
                            default=Abs(F("total_amount")),
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                    ),
                    default=Value(
                        0,
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    ),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .values("source_account_id")
            .annotate(balance=Sum("pretty_total"))
            .values("balance")[:1]
        )

        # Subquery to calculate sum of pretty_total grouped by destination_account_id
        destination_balance_subquery = (
            Transaction.objects.filter(
                destination_account_id=OuterRef("pk"),
                status_id__in=[2, 3],  # Adjust status conditions as needed
            )
            .annotate(
                pretty_total=Case(
                    When(transaction_type_id=2, then=Abs(F("total_amount"))),
                    When(transaction_type_id=1, then=-Abs(F("total_amount"))),
                    When(
                        transaction_type_id=3,
                        then=Case(
                            When(
                                destination_account_id=OuterRef("pk"),
                                then=Abs(F("total_amount")),
                            ),
                            default=Abs(F("total_amount")),
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                    ),
                    default=Value(
                        0,
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    ),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .values("destination_account_id")
            .annotate(balance=Sum("pretty_total"))
            .values("balance")[:1]
        )

        qs = qs.annotate(
            rewards_amount=Value(
                rewards_total_amount,
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )

        qs = qs.annotate(
            source_balance=Coalesce(
                Subquery(
                    source_balance_subquery,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Value(
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            ),
            destination_balance=Coalesce(
                Subquery(
                    destination_balance_subquery,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Value(
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            ),
        ).annotate(
            balance=ExpressionWrapper(
                F("source_balance")
                + F("destination_balance")
                + F("opening_balance")
                + F("archive_balance"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        pending_balance = (
            Transaction.objects.filter(
                Q(source_account_id=account_id)
                | Q(destination_account_id=account_id),
                transaction_date__lte=today,
                status_id=1,
            )
            .annotate(
                pretty_total=Case(
                    When(transaction_type_id=2, then=Abs(F("total_amount"))),
                    When(transaction_type_id=1, then=-Abs(F("total_amount"))),
                    When(
                        transaction_type_id=3,
                        then=Case(
                            When(
                                destination_account_id=OuterRef("pk"),
                                then=Abs(F("total_amount")),
                            ),
                            default=Abs(F("total_amount")),
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                    ),
                    default=Value(
                        0,
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    ),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .values("destination_account_id")
            .annotate(balance=Sum("pretty_total"))
            .values("balance")[:1]
        )
        qs = qs.annotate(
            available_credit=Coalesce(
                ExpressionWrapper(
                    F("credit_limit")
                    - Abs(F("balance"))
                    - Abs(pending_balance),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Value(
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            )
        )

        account = qs.first()
        api_logger.debug(f"Account retrieved : {account.account_name}")
        acc_out = AccountOut.from_orm(account)
        acc_out.due_date = due_date
        acc_out.statement_date = statement_date
        acc_out.current_yr_rewards = last_six_month_reward_amounts(account_id)
        acc_out.last_yr_rewards = last_year_six_month_reward_amounts(account_id)

        return acc_out
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Account not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@account_router.get("/list", response=List[AccountOut])
def list_accounts(request, query: AccountQuery = Query(...)):
    """
    The function `list_accounts` retrieves a list of accounts,
    optionally filtered by inactive or account type.

    Args:
        request (HttpRequest): The HTTP request object.
        account_type (int): Optional account type id to filter accounts.
        inactive (bool): Optional filter on inactive or not

    Returns:
        AccountOut: a list of Account objects
    """

    try:
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

        # Subquery to calculate sum of pretty_total grouped by source_account_id
        source_balance_subquery = (
            Transaction.objects.filter(
                source_account_id=OuterRef("pk"),
                status_id__in=[2, 3],  # Adjust status conditions as needed
            )
            .annotate(
                pretty_total=Case(
                    When(transaction_type_id=2, then=Abs(F("total_amount"))),
                    When(transaction_type_id=1, then=-Abs(F("total_amount"))),
                    When(
                        transaction_type_id=3,
                        then=Case(
                            When(
                                source_account_id=OuterRef("pk"),
                                then=-Abs(F("total_amount")),
                            ),
                            default=Abs(F("total_amount")),
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                    ),
                    default=Value(
                        0,
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    ),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .values("source_account_id")
            .annotate(balance=Sum("pretty_total"))
            .values("balance")[:1]
        )

        # Subquery to calculate sum of pretty_total grouped by destination_account_id
        destination_balance_subquery = (
            Transaction.objects.filter(
                destination_account_id=OuterRef("pk"),
                status_id__in=[2, 3],  # Adjust status conditions as needed
            )
            .annotate(
                pretty_total=Case(
                    When(transaction_type_id=2, then=Abs(F("total_amount"))),
                    When(transaction_type_id=1, then=-Abs(F("total_amount"))),
                    When(
                        transaction_type_id=3,
                        then=Case(
                            When(
                                destination_account_id=OuterRef("pk"),
                                then=Abs(F("total_amount")),
                            ),
                            default=Abs(F("total_amount")),
                            output_field=DecimalField(
                                max_digits=12, decimal_places=2
                            ),
                        ),
                    ),
                    default=Value(
                        0,
                        output_field=DecimalField(
                            max_digits=12, decimal_places=2
                        ),
                    ),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                )
            )
            .values("destination_account_id")
            .annotate(balance=Sum("pretty_total"))
            .values("balance")[:1]
        )

        # Annotate the Account queryset with the combined balance
        qs = qs.annotate(
            source_balance=Coalesce(
                Subquery(
                    source_balance_subquery,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Value(
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            ),
            destination_balance=Coalesce(
                Subquery(
                    destination_balance_subquery,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Value(
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            ),
        ).annotate(
            balance=ExpressionWrapper(
                F("source_balance")
                + F("destination_balance")
                + F("opening_balance")
                + F("archive_balance"),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        api_logger.debug("Account list retrieved")
        return qs
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Account list retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error : {str(e)}")


@account_router.patch("/update/{account_id}")
def update_account(request, account_id: int, payload: AccountUpdate):
    """
    The function `update_account` updates the account specified by id,
    patching the account if a field is sent in the payload.

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): the id of the account to update
        payload (AccountUpdate): an account update object

    Returns:
        success: True

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:
        account = get_object_or_404(Account, id=account_id)

        apply_patch(account, payload, exclude={"rewards_amount"})

        if "rewards_amount" in payload.__fields_set__:
            Reward.objects.create(
                reward_amount=payload.rewards_amount,
                reward_account_id=account_id,
            )

        if payload.calculate_payments is False:
            account.payment_strategy = "F"
            account.payment_amount = 0.00
            account.minimum_payment_amount = 0.00
            account.funding_account = None

        account.save()
        api_logger.info(f"Account updated : {account.account_name}")
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Account not updated : account exists ({payload.account_name})"
            )
            error_logger.error(
                f"Account not updated : account exists ({payload.account_name})"
            )
            raise HttpError(400, "Account already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Account not updated : db integrity error")
            error_logger.error("Account not updated : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Account not updated")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record update error: {str(e)}")


@account_router.delete("/delete/{account_id}")
def delete_account(request, account_id: int):
    """
    The function `delete_account` deletes the account specified by id,
    and any related transaction details and transactions.

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): the id of the account to delete

    Returns:
        success: True

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:
        # Retrieve the account
        account = get_object_or_404(Account, id=account_id)
        account_name = account.account_name

        # Delete the related transactions
        transactions = Transaction.objects.filter(
            source_account=account
        ).exclude(transaction_type__id=3)
        transactions.delete()

        # Delete account
        account.delete()

        api_logger.info(
            f"Account deleted (and related transactions/details) : {account_name}"
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Account not deleted")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


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
