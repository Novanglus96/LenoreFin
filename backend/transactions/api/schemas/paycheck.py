from ninja import Schema
from decimal import Decimal
from pydantic import BaseModel, Field
from administration.api.schemas.payee import PayeeOut


# The class PayCheckIn is a schema for validating Paycheck information.
class PaycheckIn(Schema):
    gross: Decimal = Field(whole_digits=10, decimal_places=2)
    net: Decimal = Field(whole_digits=10, decimal_places=2)
    taxes: Decimal = Field(whole_digits=10, decimal_places=2)
    health: Decimal = Field(whole_digits=10, decimal_places=2)
    pension: Decimal = Field(whole_digits=10, decimal_places=2)
    fsa: Decimal = Field(whole_digits=10, decimal_places=2)
    dca: Decimal = Field(whole_digits=10, decimal_places=2)
    union_dues: Decimal = Field(whole_digits=10, decimal_places=2)
    four_fifty_seven_b: Decimal = Field(whole_digits=10, decimal_places=2)
    payee_id: int


# The class PayCheckOut is a schema for representing Paycheck information.
class PaycheckOut(Schema):
    id: int
    gross: Decimal = Field(whole_digits=10, decimal_places=2)
    net: Decimal = Field(whole_digits=10, decimal_places=2)
    taxes: Decimal = Field(whole_digits=10, decimal_places=2)
    health: Decimal = Field(whole_digits=10, decimal_places=2)
    pension: Decimal = Field(whole_digits=10, decimal_places=2)
    fsa: Decimal = Field(whole_digits=10, decimal_places=2)
    dca: Decimal = Field(whole_digits=10, decimal_places=2)
    union_dues: Decimal = Field(whole_digits=10, decimal_places=2)
    four_fifty_seven_b: Decimal = Field(whole_digits=10, decimal_places=2)
    payee: PayeeOut
