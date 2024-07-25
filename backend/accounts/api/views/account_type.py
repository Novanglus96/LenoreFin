from ninja import Router
from django.db import IntegrityError
from ninja.errors import HttpError
from accounts.models import AccountType
from accounts.api.schemas.account_type import AccountTypeIn, AccountTypeOut
from administration.models import logToDB
from django.shortcuts import get_object_or_404

account_type_router = Router()


@account_type_router.post("/accounts/types")
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


@account_type_router.get(
    "/accounts/types/{accounttype_id}", response=AccountTypeOut
)
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
