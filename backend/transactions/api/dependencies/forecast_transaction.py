from datetime import datetime
from typing import List
from tags.api.dependencies.custom_tag import CustomTag


class ForecastTransaction:

    def __init__(
        self,
        transaction_date: datetime.date,
        total_amount: float,
        status_id: int,
        memo: str,
        description: str,
        edit_date: datetime.date,
        add_date: datetime.date,
        transaction_type_id: int,
        paycheck_id: int,
        source_account_id: int,
        destination_account_id: int,
        tags: List[CustomTag],
        checkNumber: int,
        source_name: str,
        destination_name: str,
        pretty_account: str,
        pretty_total: float,
        custom_ordering: int,
        cumulative_balance: float,
        balance: float,
    ):
        self.transaction_date = transaction_date
        self.total_amount = total_amount
        self.status_id = status_id
        self.memo = memo
        self.description = description
        self.edit_date = edit_date
        self.add_date = add_date
        self.transaction_type_id = transaction_type_id
        self.paycheck_id = paycheck_id
        self.source_account_id = source_account_id
        self.destination_account_id = destination_account_id
        self.tags = tags
        self.checkNumber = checkNumber
        self.source_name = source_name
        self.destination_name = destination_name
        self.pretty_account = pretty_account
        self.custom_ordering = custom_ordering
        self.cumulative_balance = cumulative_balance
        self.balance = balance

    def __str__(self):
        return (
            f"ForecastTransaction(transaction_date={self.transaction_date}, "
            + f"total_amount={self.total_amount}, "
            + f"status_id={self.status_id}, "
            + f"memo={self.memo}, "
            + f"description={self.description}, "
            + f"edit_date={self.edit_date}, "
            + f"add_date={self.add_date}, "
            + f"transaction_type_id={self.transaction_type_id}, "
            + f"paycheck_id={self.paycheck_id}, "
            + f"source_account_id={self.source_account_id}, "
            + f"destination_account_id={self.destination_account_id}, "
            + f"tags={self.tags}, "
            + f"checkNumber={self.checkNumber}), "
            + f"source_name={self.source_name}) ,"
            + f"destination_name={self.destination_name}) ,"
            + f"pretty_account={self.pretty_account}) ,"
            + f"custom_ordering={self.custom_ordering}) ,"
            + f"cumulative_balance={self.cumulative_balance}) ,"
            + f"balance={self.balance})"
        )
