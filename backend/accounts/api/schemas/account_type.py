from ninja import Schema
from pydantic import ConfigDict


# The class AccountTypeIn is a schema for validating account types.
class AccountTypeIn(Schema):
    account_type: str
    color: str
    icon: str


# The class AccountTypeOut is a schema for representing account types.
class AccountTypeOut(Schema):
    id: int
    account_type: str
    color: str
    icon: str

    model_config = ConfigDict(from_attributes=True)
