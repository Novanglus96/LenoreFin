from ninja import Schema


# The class BankIn is a schema for validating banks.
class BankIn(Schema):
    bank_name: str


# The class BankOut is a schema for representing banks.
class BankOut(Schema):
    id: int
    bank_name: str
