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
from utils.apply_patch import apply_patch
from accounts.services import (
    get_account_financials,
    AccountNotFound,
    list_accounts_with_financials,
)
from accounts.mappers import domain_account_to_schema
import logging
from administration.api.dependencies.auth import FullAccessAuth

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


account_router = Router(tags=["Accounts"])


@account_router.post("/create", auth=FullAccessAuth())
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
        result = get_account_financials(account_id)

        return domain_account_to_schema(result)

    except AccountNotFound:
        raise HttpError(404, "Account not found")

    except Exception as e:
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
        domain_accounts = list_accounts_with_financials(query)
        schema_accounts = []

        # Get Account financials
        for account in domain_accounts:
            schema_accounts.append(domain_account_to_schema(account))

        api_logger.debug("Account list retrieved")
        return schema_accounts
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Account list retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error : {str(e)}")


@account_router.patch("/update/{account_id}", auth=FullAccessAuth())
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

        if account.parent_account_id:
            if account.calculate_interest:
                raise HttpError(400, "A child account cannot have interest calculations enabled.")
            if account.annual_rate and account.annual_rate != 0:
                raise HttpError(400, "A child account cannot have an APY set.")

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


@account_router.delete("/delete/{account_id}", auth=FullAccessAuth())
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
