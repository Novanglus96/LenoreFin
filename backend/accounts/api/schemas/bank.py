from ninja import Schema
from pydantic import ConfigDict
from typing import Optional


# The class BankIn is a schema for validating banks.
class BankIn(Schema):
    bank_name: str
    logo_url: Optional[str] = None


# The class BankOut is a schema for representing banks.
class BankOut(Schema):
    id: int
    bank_name: str
    logo_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
