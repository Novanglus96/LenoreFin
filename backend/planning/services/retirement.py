import ast
from datetime import date, datetime
from administration.models import Option
from accounts.models import Account
from transactions.services import get_account_transactions_and_balances
from utils.dates import (
    get_dates_in_range,
    get_forecast_end_date,
    get_forecast_start_date,
    get_todays_date_timezone_adjusted,
)
from planning.dto import DomainForecast, DomainDataSetObject

COLORS = [
    "#7fb1b1", "#597c7c", "#7f8cb1", "#7fb17f", "#597c59",
    "#b17fa5", "#7c5973", "#b1a77f", "#edffff", "#dbffff",
    "#7c6759", "#b1937f", "#8686b1", "#5e5e7c", "#757c59",
    "#52573e", "#ffedff", "#573e57", "#fff8db", "#ffe9db",
    "#e0e0ff", "#9d9db3",
]


def get_retirement_forecast() -> DomainForecast:
    try:
        retirement_accounts_string = Option.objects.get(id=1).retirement_accounts
        retirement_array = ast.literal_eval(retirement_accounts_string)
        if not isinstance(retirement_array, list):
            retirement_array = []
    except (Option.DoesNotExist, ValueError, SyntaxError):
        retirement_array = []

    today = get_todays_date_timezone_adjusted()
    jan_1st = date(today.year, 1, 1)
    dec_31st = date(today.year, 12, 31)
    start_interval = (today - jan_1st).days
    end_interval = (dec_31st - today).days

    labels = get_dates_in_range(start_interval, end_interval)
    start_date = get_forecast_start_date(start_interval)
    end_date = get_forecast_end_date(end_interval)

    account_info = []
    for account_id in retirement_array:
        account_obj = Account.objects.get(id=account_id)
        transactions_list, previous_balance = get_account_transactions_and_balances(
            end_date, account_id, True, True, start_date, False
        )
        account_info.append({
            "id": account_id,
            "name": account_obj.account_name,
            "transactions": transactions_list,
            "previous_balance": previous_balance,
            "data": [],
        })

    totals = []
    for label_date in labels:
        parsed_date = datetime.strptime(label_date, "%b %d, %y")
        formatted_date = parsed_date.strftime("%Y-%m-%d")
        today_total = 0
        for account in account_info:
            transactions_today = [
                t for t in account["transactions"]
                if str(t["transaction_date"] if isinstance(t, dict) else t.transaction_date) == formatted_date
            ]
            if transactions_today:
                last = transactions_today[-1]
                daily_total = last["balance"] if isinstance(last, dict) else last.balance
            else:
                daily_total = account["previous_balance"]
            account["previous_balance"] = daily_total
            account["data"].append(daily_total)
            today_total += daily_total
        totals.append(today_total)

    datasets = [
        DomainDataSetObject(
            borderColor="#06966A",
            backgroundColor="#06966A",
            tension=0.1,
            data=totals,
            pointStyle="line",
            radius=2,
            hitRadius=5,
            hoverRadius=5,
            label="Total",
        )
    ]
    for index, account in enumerate(account_info):
        color = COLORS[index % len(COLORS)]
        datasets.append(DomainDataSetObject(
            borderColor=color,
            backgroundColor=color,
            tension=0.1,
            data=account["data"],
            pointStyle="line",
            radius=2,
            hitRadius=5,
            hoverRadius=5,
            label=account["name"],
        ))

    return DomainForecast(labels=labels, datasets=datasets)
