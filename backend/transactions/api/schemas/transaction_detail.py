from ninja import Schema
from pydantic import ConfigDict, condecimal
from tags.api.schemas.tag import TagOut

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


# The class TransactionDetailOut is a schema for representing Transaction Details.
class TransactionDetailOut(Schema):
    id: int
    transaction: "TransactionOut"
    detail_amt: AmountDecimal
    tag: TagOut
    full_toggle: bool

    model_config = ConfigDict(from_attributes=True)


from transactions.api.schemas.transaction import TransactionOut  # noqa: E402

TransactionDetailOut.update_forward_refs()


# The class TransactionDetailIn is a schema for validating Transaction Details.
class TransactionDetailIn(Schema):
    transaction_id: int
    account_id: int
    detail_amt: AmountDecimal
    tag_id: int
    full_toggle: bool
