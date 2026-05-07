from ninja import Schema
from pydantic import ConfigDict, condecimal
from administration.api.schemas.payee import PayeeOut

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


# The class PayCheckIn is a schema for validating Paycheck information.
class PaycheckIn(Schema):
    gross: AmountDecimal
    net: AmountDecimal
    taxes: AmountDecimal
    health: AmountDecimal
    pension: AmountDecimal
    fsa: AmountDecimal
    dca: AmountDecimal
    union_dues: AmountDecimal
    four_fifty_seven_b: AmountDecimal
    payee_id: int


# The class PayCheckOut is a schema for representing Paycheck information.
class PaycheckOut(Schema):
    id: int
    gross: AmountDecimal
    net: AmountDecimal
    taxes: AmountDecimal
    health: AmountDecimal
    pension: AmountDecimal
    fsa: AmountDecimal
    dca: AmountDecimal
    union_dues: AmountDecimal
    four_fifty_seven_b: AmountDecimal
    payee: PayeeOut

    model_config = ConfigDict(from_attributes=True)
