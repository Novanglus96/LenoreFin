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
from planning.api.schemas.retirement import RetirementTransactionOut

COLORS = [
    "#7fb1b1", "#597c7c", "#7f8cb1", "#7fb17f", "#597c59",
    "#b17fa5", "#7c5973", "#b1a77f", "#edffff", "#dbffff",
    "#7c6759", "#b1937f", "#8686b1", "#5e5e7c", "#757c59",
    "#52573e", "#ffedff", "#573e57", "#fff8db", "#ffe9db",
    "#e0e0ff", "#9d9db3",
]


def _hex_to_rgba(hex_color: str, alpha: float = 0.5) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _get_retirement_account_ids() -> list:
    try:
        option = Option.load()
        retirement_accounts_string = option.retirement_accounts if option else None
        if not retirement_accounts_string:
            return []
        retirement_array = ast.literal_eval(retirement_accounts_string)
        return retirement_array if isinstance(retirement_array, list) else []
    except (Option.DoesNotExist, ValueError, SyntaxError):
        return []


def get_retirement_forecast() -> DomainForecast:
    retirement_array = _get_retirement_account_ids()

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
            fill=False,
        )
    ]
    for index, account in enumerate(account_info):
        border_color = COLORS[index % len(COLORS)]
        bg_color = _hex_to_rgba(border_color, 0.5)
        datasets.append(DomainDataSetObject(
            borderColor=border_color,
            backgroundColor=bg_color,
            tension=0.1,
            data=account["data"],
            pointStyle="line",
            radius=2,
            hitRadius=5,
            hoverRadius=5,
            label=account["name"],
            fill=True,
        ))

    return DomainForecast(labels=labels, datasets=datasets)


def get_retirement_transactions() -> list:
    retirement_array = _get_retirement_account_ids()
    if not retirement_array:
        return []

    today = get_todays_date_timezone_adjusted()
    jan_1st = date(today.year, 1, 1)
    dec_31st = date(today.year, 12, 31)
    start_interval = (today - jan_1st).days
    end_interval = (dec_31st - today).days
    start_date = get_forecast_start_date(start_interval)
    end_date = get_forecast_end_date(end_interval)

    results = []
    for account_id in retirement_array:
        try:
            account_obj = Account.objects.get(id=account_id)
        except Account.DoesNotExist:
            continue

        transactions_list, _ = get_account_transactions_and_balances(
            end_date, account_id, False, True, start_date, False
        )
        for t in transactions_list:
            if isinstance(t, dict):
                status = t.get("status") or {}
                txn_type = t.get("transaction_type") or {}
                results.append(RetirementTransactionOut(
                    transaction_date=t["transaction_date"],
                    account_name=account_obj.account_name,
                    description=t.get("description", ""),
                    total_amount=t.get("total_amount", 0),
                    balance=t.get("balance"),
                    status_name=status.get("transaction_status", "") if isinstance(status, dict) else getattr(status, "transaction_status", ""),
                    transaction_type_name=txn_type.get("transaction_type", "") if isinstance(txn_type, dict) else getattr(txn_type, "transaction_type", ""),
                ))
            else:
                results.append(RetirementTransactionOut(
                    transaction_date=t.transaction_date,
                    account_name=account_obj.account_name,
                    description=t.description,
                    total_amount=t.total_amount,
                    balance=t.balance,
                    status_name=t.status.transaction_status if t.status else "",
                    transaction_type_name=t.transaction_type.transaction_type if t.transaction_type else "",
                ))

    results.sort(key=lambda x: x.transaction_date)
    return results
