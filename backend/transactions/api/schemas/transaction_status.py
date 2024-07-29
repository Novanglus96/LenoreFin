from ninja import Schema


# The class TransactionStatusIn is a schema for validating transaction status.
class TransactionStatusIn(Schema):
    transaction_status: str


# The class TransactionStatusOut is a schema for representing transaction status.
class TransactionStatusOut(Schema):
    id: int
    transaction_status: str
