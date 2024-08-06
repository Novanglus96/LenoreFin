from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from accounts.models import Account, Reward
from transactions.models import Transaction, TransactionDetail
from accounts.api.schemas.account import AccountIn, AccountOut, AccountUpdate
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
        logToDB(
            f"Account created : {account.account_name}",
            account.id,
            None,
            None,
            3001001,
            1,
        )
        return {"id": account.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Account not created : name exists ({payload.account_name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Account name already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Account not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
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

        qs = qs.annotate(
            available_credit=Coalesce(
                ExpressionWrapper(
                    F("credit_limit") - Abs(F("balance")),
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
                Value(
                    0,
                    output_field=DecimalField(max_digits=12, decimal_places=2),
                ),
            )
        )
        account = qs.first()
        logToDB(
            f"Account retrieved : {account.account_name}",
            account_id,
            None,
            None,
            3001006,
            1,
        )
        return account
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account not retrieved : {str(e)}",
            account_id,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@account_router.get("/list", response=List[AccountOut])
def list_accounts(
    request,
    account_type: Optional[int] = Query(None),
    inactive: Optional[bool] = Query(None),
):
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
        if not inactive:
            qs = qs.filter(active=True)

        # If account type argument is provided, filter by account type
        if account_type is not None and account_type != 0:
            qs = qs.filter(account_type__id=account_type)

        if account_type is not None and account_type == 0:
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
        logToDB(
            "Account list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return qs
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
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
        if payload.account_name is not None:
            account.account_name = payload.account_name
        if payload.account_type_id is not None:
            account.account_type_id = payload.account_type_id
        if payload.opening_balance is not None:
            account.opening_balance = payload.opening_balance
        if payload.apy is not None:
            account.apy = payload.apy
        if payload.due_date is not None:
            account.due_date = payload.due_date
        if payload.active is not None:
            account.active = payload.active
        if payload.open_date is not None:
            account.open_date = payload.open_date
        if payload.next_cycle_date is not None:
            account.next_cycle_date = payload.next_cycle_date
        if payload.statement_cycle_length is not None:
            account.statement_cycle_length = payload.statement_cycle_length
        if payload.statement_cycle_period is not None:
            account.statement_cycle_period = payload.statement_cycle_period
        if payload.rewards_amount is not None:
            Reward.objects.create(
                reward_amount=payload.rewards_amount,
                reward_account_id=account_id,
            )
        if payload.credit_limit is not None:
            account.credit_limit = payload.credit_limit
        if payload.bank_id is not None:
            account.bank_id = payload.bank_id
        if payload.last_statement_amount is not None:
            account.last_statement_amount = payload.last_statement_amount
        account.save()
        logToDB(
            f"Account updated : {account.account_name}",
            account_id,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Account not updated : account exists ({payload.account_name})",
                account_id,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Account already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Account not updated : db integrity error",
                account_id,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account not updated : {str(e)}",
            account_id,
            None,
            None,
            3001902,
            2,
        )
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

        logToDB(
            f"Account deleted (and related transactions/details) : {account_name}",
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
            f"Account not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")
