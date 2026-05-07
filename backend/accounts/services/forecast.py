from datetime import datetime
from utils.dates import (
    get_dates_in_range,
    get_forecast_end_date,
    get_forecast_start_date,
)
from transactions.services import get_account_transactions_and_balances
from accounts.dto import (
    DomainForecast,
    DomainDatasetObject,
    DomainFillObject,
    DomainTargetObject,
)


def get_account_forecast(
    account_id: int, start_interval: int, end_interval: int
) -> DomainForecast:
    labels = get_dates_in_range(start_interval, end_interval)
    start_date = get_forecast_start_date(start_interval)
    end_date = get_forecast_end_date(end_interval)

    transactions_list, previous_balance = get_account_transactions_and_balances(
        end_date, account_id, True, True, start_date, False
    )

    data = []
    daily_total = previous_balance

    for label_date in labels:
        parsed_date = datetime.strptime(label_date, "%b %d, %y")
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        transactions_today = [
            t for t in transactions_list
            if str(t["transaction_date"] if isinstance(t, dict) else t.transaction_date) == formatted_date
        ]
        if transactions_today:
            last = transactions_today[-1]
            daily_total = last["balance"] if isinstance(last, dict) else last.balance
        previous_balance = daily_total
        data.append(daily_total)

    fill = DomainFillObject(
        target=DomainTargetObject(value=0),
        above="rgb(76, 175, 80)",
        below="rgb(248, 121, 121)",
    )
    dataset = DomainDatasetObject(
        borderColor="#06966A",
        backgroundColor="#06966A",
        tension=0.1,
        data=data,
        fill=fill,
        pointStyle="circle",
        radius=2,
        hitRadius=5,
        hoverRadius=5,
    )
    return DomainForecast(labels=labels, datasets=[dataset])
