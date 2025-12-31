from administration.dto import DomainPayee
from administration.api.schemas.payee import PayeeOut


def domain_payee_to_schema(
    pay: DomainPayee,
) -> PayeeOut:
    return PayeeOut(id=pay.id, payee_name=pay.payee_name)
