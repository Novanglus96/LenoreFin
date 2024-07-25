from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from accounts.models import AccountType
from accounts.api.schemas.account_type import AccountTypeIn, AccountTypeOut
from administration.models import logToDB
from django.shortcuts import get_object_or_404
from typing import List

account_type_router = Router(tags=["Account Types"])


@account_type_router.post("/create")
def create_account_type(request, payload: AccountTypeIn):
    """
    The function `create_account_type` creates an account type

    Args:
        request ():
        payload (AccountTypeIn): An object using schema of AccountTypeIn.

    Returns:
        id: returns the id of the created account type
    """

    try:
        account_type = AccountType.objects.create(**payload.dict())
        logToDB(
            f"Account type created : {account_type.account_type}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": account_type.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Account type not created : type exists ({payload.account_type})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Account type already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Account type not created : db integrity error",
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
            f"Account type not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@account_type_router.get("/get/{accounttype_id}", response=AccountTypeOut)
def get_account_type(request, accounttype_id: int):
    """
    The function `get_account_type` retrieves the account type by id

    Args:
        request (HttpRequest): The HTTP request object
        accounttype_id (int): The id of the account type to retrieve.

    Returns:
        AccountTypeOut: the account type object

    Raises:
        Http404: If the account type with the specified ID does not exist.
    """

    try:
        account_type = get_object_or_404(AccountType, id=accounttype_id)
        logToDB(
            f"Account type retrieved : {account_type.account_type}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return account_type
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Account type not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@account_type_router.get("/list", response=List[AccountTypeOut])
def list_account_types(request):
    """
    The function `list_account_types` retrieves a list of account types,
    orderd by ID ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        AccountTypeOut: a list of account type objects
    """

    try:
        qs = AccountType.objects.all().order_by("id")
        logToDB(
            "Account type list retrieved",
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
            f"Account type list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, "Record retrieval error")


@account_type_router.put("/update/{accounttype_id}")
def update_account_type(request, accounttype_id: int, payload: AccountTypeIn):
    """
    The function `update_account_type` updates the account type specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        accounttype_id (int): the id of the account type to update
        payload (AccountTypeIn): an account type object

    Returns:
        success: True

    Raises:
        Http404: If the account type with the specified ID does not exist.
    """

    try:
        account_type = get_object_or_404(AccountType, id=accounttype_id)
        account_type.account_type = payload.account_type
        account_type.color = payload.color
        account_type.icon = payload.icon
        account_type.save()
        logToDB(
            f"Account type updated : {account_type.account_type}",
            None,
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
                f"Account type not updated : account type exists ({payload.account_type})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Account type already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Account type not updated : db integrity error",
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
            f"Account type not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@account_type_router.delete("/delete/{accounttype_id}")
def delete_account_type(request, accounttype_id: int):
    """
    The function `delete_account_type` deletes the account type specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        accounttype_id (int): the id of the account type to delete

    Returns:
        success: True

    Raises:
        Http404: If the account type with the specified ID does not exist.
    """

    try:
        account_type = get_object_or_404(AccountType, id=accounttype_id)
        account_type_name = account_type.account_type
        account_type.delete()
        logToDB(
            f"Account type deleted : {account_type_name}",
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
            f"Account type not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")
