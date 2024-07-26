from ninja import Schema


# The class TransactionTypeIn is a schema for validating transaction types.
class TransactionTypeIn(Schema):
    transaction_type: str


# The class TransactionTypeOut is a schema for representing transaction types.
class TransactionTypeOut(Schema):
    id: int
    transaction_type: str
