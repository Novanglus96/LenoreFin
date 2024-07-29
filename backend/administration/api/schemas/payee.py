from ninja import Schema


# The class PayeeIn is a schema for validating payee information.
class PayeeIn(Schema):
    payee_name: str


# The class PayeeOut is a schema for representing payee information.
class PayeeOut(Schema):
    id: int
    payee_name: str
