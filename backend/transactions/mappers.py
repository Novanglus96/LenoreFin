from transactions.dto import (
    DomainTransaction,
    DomainTransactionDetail,
    DomainTransactionStatus,
    DomainTransactionType,
    DomainPaycheck,
)
from transactions.api.schemas.transaction import (
    TransactionOut,
    TransactionDetailOut,
    TransactionStatusOut,
    TransactionTypeOut,
    PaycheckOut,
)
from administration.mappers import domain_payee_to_schema
from tags.mappers import domain_tag_to_schema


def domain_transaction_to_schema(
    tx: DomainTransaction,
) -> TransactionOut:
    return TransactionOut(
        id=tx.id,
        transaction_date=tx.transaction_date,
        total_amount=tx.total_amount,
        status=domain_transaction_status_to_schema(tx.status),
        memo=tx.memo,
        description=tx.description,
        edit_date=tx.edit_date,
        add_date=tx.add_date,
        transaction_type=domain_transaction_type_to_schema(tx.transaction_type),
        paycheck=(
            domain_paycheck_to_schema(tx.paycheck) if tx.paycheck else None
        ),
        balance=tx.balance,
        pretty_account=tx.pretty_account,
        tags=tx.tags,
        details=(
            [domain_transaction_detail_to_schema(d) for d in tx.details]
            if tx.details
            else []
        ),
        pretty_total=tx.pretty_total,
        source_account_id=tx.source_account_id,
        destination_account_id=tx.destination_account_id,
        checkNumber=tx.checkNumber,
        reminder_id=tx.reminder_id,
        tag_total=tx.tag_total,
        simulated=tx.simulated,
    )


def domain_transaction_detail_to_schema(
    detail: DomainTransactionDetail,
) -> TransactionDetailOut:
    return TransactionDetailOut(
        id=detail.id,
        transaction=domain_transaction_to_schema(detail.transaction),
        detail_amt=detail.detail_amt,
        tag=domain_tag_to_schema(detail.tag),
        full_toggle=detail.full_toggle,
    )


def domain_transaction_status_to_schema(
    status: DomainTransactionStatus,
) -> TransactionStatusOut:
    return TransactionStatusOut(
        id=status.id, transaction_status=status.transaction_status
    )


def domain_transaction_type_to_schema(
    type: DomainTransactionType,
) -> TransactionTypeOut:
    return TransactionTypeOut(
        id=type.id, transaction_type=type.transaction_type
    )


def domain_paycheck_to_schema(
    pay: DomainPaycheck,
) -> PaycheckOut:
    return PaycheckOut(
        id=pay.id,
        gross=pay.gross,
        net=pay.net,
        taxes=pay.taxes,
        health=pay.health,
        pension=pay.pension,
        fsa=pay.fsa,
        dca=pay.dca,
        union_dues=pay.union_dues,
        four_fifty_seven_b=pay.four_fifty_seven_b,
        payee=domain_payee_to_schema(pay.payee),
    )
