from ninja import Router, Query
from django.db import IntegrityError
from django.core.cache import cache
from ninja.errors import HttpError
from accounts.models import Account, AccountFavorite, Reward
from transactions.models import Transaction
from accounts.api.schemas.investment_return import InvestmentReturnOut
from accounts.services import calculate_investment_return
from accounts.api.schemas.account import (
    AccountIn,
    AccountOut,
    AccountUpdate,
    AccountQuery,
    FavoriteBalanceSummary,
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
from core.cache.keys import account_financials as account_financials_key
import logging
from administration.api.dependencies.auth import FullAccessAuth
from transactions.services import get_account_transactions_and_balances
from utils.dates import get_todays_date_timezone_adjusted
from dateutil.relativedelta import relativedelta
from datetime import timedelta

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")


account_router = Router(tags=["Accounts"])


def _safe_user(request):
    try:
        user = request.user
        return user if isinstance(getattr(user, "pk", None), int) else None
    except AttributeError:
        return None


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
            error_logger.exception(
                f"Account not created : name exists ({payload.account_name})"
            )
            raise HttpError(400, "Account name already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Account not created : db integrity error")
            error_logger.exception("Account not created : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Account not created")
        error_logger.exception(f"{str(e)}")
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
        result = get_account_financials(account_id, user=_safe_user(request))
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
        user = _safe_user(request)
        domain_accounts = list_accounts_with_financials(query, user=user)
        schema_accounts = [domain_account_to_schema(a) for a in domain_accounts]
        api_logger.debug("Account list retrieved")
        return schema_accounts
    except Exception as e:
        api_logger.error("Account list not retrieved")
        error_logger.exception(f"{str(e)}")
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
            error_logger.exception(
                f"Account not updated : account exists ({payload.account_name})"
            )
            raise HttpError(400, "Account already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Account not updated : db integrity error")
            error_logger.exception("Account not updated : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Account not updated")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Record update error: {str(e)}")


@account_router.post("/toggle-favorite/{account_id}")
def toggle_favorite(request, account_id: int):
    """
    Toggles this account as a favorite for the requesting user.
    Each user has their own independent set of favorites.
    """
    try:
        user = _safe_user(request)
        if not user:
            raise HttpError(401, "Authentication required")
        account = get_object_or_404(Account, id=account_id)
        fav, created = AccountFavorite.objects.get_or_create(user=user, account=account)
        if not created:
            fav.delete()
            is_fav = False
        else:
            is_fav = True
        cache.delete(f"{account_financials_key(account_id)}:{user.pk}")
        api_logger.info(f"Account favorite toggled : {account.account_name} -> {is_fav} (user {user.pk})")
        return {"is_favorite": is_fav}
    except HttpError:
        raise
    except Exception as e:
        api_logger.error("Account favorite not toggled")
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Toggle error: {str(e)}")


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
        error_logger.exception(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@account_router.get("/favorite-balances", response=List[FavoriteBalanceSummary])
def get_favorite_balances(request):
    """
    Returns current balance and projected 1st-of-next-month balance
    for all active favorite accounts.
    """
    try:
        user = _safe_user(request)
        if not user:
            return []

        today = get_todays_date_timezone_adjusted()
        first_of_next_month = today.replace(day=1) + relativedelta(months=1)
        # Query through the 2nd so transactions dated ON the 1st are included
        # (the service filter is transaction_date__lt=end_date)
        end_date = first_of_next_month + timedelta(days=1)

        favorite_ids = AccountFavorite.objects.filter(user=user).values_list("account_id", flat=True)
        accounts = Account.objects.filter(id__in=favorite_ids, active=True).select_related(
            "account_type", "bank"
        )

        result = []
        for account in accounts:
            try:
                financials = get_account_financials(account.id, today)
                current_balance = financials.balance
            except Exception:
                current_balance = None

            try:
                transactions, previous_balance = get_account_transactions_and_balances(
                    end_date=end_date,
                    account_id=account.id,
                    totals_only=True,
                    forecast=True,
                    start_date=today,
                )
                projected_balance = previous_balance
                for t in transactions:
                    pt = t["pretty_total"] if isinstance(t, dict) else t.pretty_total
                    if pt is not None:
                        projected_balance += pt
            except Exception as e:
                error_logger.exception(f"Projected balance error for account {account.id}: {e}")
                projected_balance = None

            result.append(
                FavoriteBalanceSummary(
                    id=account.id,
                    account_name=account.account_name,
                    account_type_id=account.account_type_id,
                    account_type_color=account.account_type.color,
                    account_type_slug=account.account_type.slug,
                    logo_url=account.bank.logo_url if account.bank else None,
                    balance=current_balance,
                    projected_balance=projected_balance,
                )
            )

        api_logger.debug("Favorite balances retrieved")
        return result
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@account_router.get("/{account_id}/investment-return", response=InvestmentReturnOut)
def get_investment_return(request, account_id: int):
    """
    Returns Modified Dietz annualised return for an investment account.
    """
    try:
        result = calculate_investment_return(account_id)
        if result is None:
            return InvestmentReturnOut(
                rate=None,
                period_months=12,
                data_points=0,
                sufficient_data=False,
            )
        return InvestmentReturnOut(
            rate=result["rate"],
            period_months=result["period_months"],
            data_points=result["data_points"],
            sufficient_data=True,
        )
    except Exception as e:
        error_logger.exception(str(e))
        raise HttpError(500, f"Record retrieval error: {str(e)}")
