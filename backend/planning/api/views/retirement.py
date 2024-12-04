from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from accounts.models import Account
from administration.models import Option
from planning.api.schemas.retirement import (
    TargetObject,
    FillObject,
    DatasetObject,
    GraphData,
    ForecastOut,
)
from administration.api.dependencies.log_to_db import logToDB
from django.shortcuts import get_object_or_404
from typing import List
from django.db.models import (
    Case,
    When,
    Q,
    IntegerField,
    Value,
    F,
    CharField,
    Sum,
    Subquery,
    OuterRef,
    FloatField,
    Window,
    ExpressionWrapper,
    DecimalField,
    Func,
    Count,
)
from django.db.models.functions import Concat, Coalesce, Abs
from typing import List, Optional, Dict, Any
from accounts.api.dependencies.get_dates_in_range import get_dates_in_range
from accounts.api.dependencies.get_unformatted_dates_in_range import (
    get_unformatted_dates_in_range,
)
from accounts.api.dependencies.get_forecast_end_date import (
    get_forecast_end_date,
)
from accounts.api.dependencies.get_forecast_start_date import (
    get_forecast_start_date,
)
from transactions.api.dependencies.get_complete_transaction_list_with_totals import (
    get_complete_transaction_list_with_totals,
)
from datetime import date, timedelta, datetime
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
import ast

retirement_router = Router(tags=["Retirement"])


@retirement_router.get("/get", response=ForecastOut)
def get_forecast(
    request,
):
    """
    The function `get_forecast` retrieves the forecast data for the retirement
    accounts

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        ForecastOut: the forecast object

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:
        # Get the retirement accounts from options
        retirement_accounts_string = Option.objects.get(
            id=1
        ).retirement_accounts
        try:
            # Attempt to parse the string into a Python list
            retirement_array = ast.literal_eval(retirement_accounts_string)
            # Ensure it's a list
            if not isinstance(retirement_array, list):
                retirement_array = []  # Not a valid list
        except (ValueError, SyntaxError):
            # Handle invalid or badly formatted strings
            retirement_array = []
        # Get start and end date of the current year
        today = get_todays_date_timezone_adjusted()

        # January 1st of the current year
        jan_1st = date(today.year, 1, 1)

        # December 31st of the current year
        dec_31st = date(today.year, 12, 31)

        # Calculate days since January 1st
        start_interval = (today - jan_1st).days

        # Calculate days until December 31st
        end_interval = (dec_31st - today).days

        # Retrieve the dates in range as labels for forecast
        labels = get_dates_in_range(start_interval, end_interval)

        dates = get_unformatted_dates_in_range(start_interval, end_interval)
        totals = []
        datasets = []

        # Retrieve the transactions in the date range for the account
        start_date = get_forecast_start_date(start_interval)
        end_date = get_forecast_end_date(end_interval)

        # Get opening balance and transactions for each account
        account_info = []
        for account in retirement_array:
            account_obj = Account.objects.get(id=account)
            opening_balance = Account.objects.get(id=account).opening_balance

            # Get list of transactions
            transactions_list, previous_balance = (
                get_complete_transaction_list_with_totals(
                    end_date, account, True, True, start_date
                )
            )
            account_dict = {
                "id": account,
                "name": account_obj.account_name,
                "opening_balance": account_obj.opening_balance,
                "transactions": transactions_list,
                "previous_balance": previous_balance,
                "data": [],
            }
            account_info.append(account_dict)

        # Get the initial balance
        # Use opening balance or first previous balance available
        daily_total = 0

        # Set Color Options
        colors = [
            "#7fb1b1",
            "#597c7c",
            "#7f8cb1",
            "#7fb17f",
            "#597c59",
            "#b17fa5",
            "#7c5973",
            "#b1a77f",
            "#edffff",
            "#dbffff",
            "#7c6759",
            "#b1937f",
            "#8686b1",
            "#5e5e7c",
            "#757c59",
            "#52573e",
            "#ffedff",
            "#573e57",
            "#fff8db",
            "#ffe9db",
            "#e0e0ff",
            "#9d9db3",
        ]

        # Get the totals by day
        for label_date in labels:
            parsed_date = datetime.strptime(label_date, "%b %d, %y")
            formatted_date = parsed_date.strftime("%Y-%m-%d")
            today_total = 0
            for account in account_info:
                transactions_today = []
                for transaction in account["transactions"]:
                    if isinstance(transaction, dict):
                        if str(transaction["transaction_date"]) == str(
                            formatted_date
                        ):
                            transactions_today.append(transaction)
                    else:
                        if str(transaction.transaction_date) == str(
                            formatted_date
                        ):
                            transactions_today.append(transaction)
                if len(transactions_today) > 0:
                    last_transaction_today = transactions_today[-1]
                    if isinstance(last_transaction_today, dict):
                        daily_total = last_transaction_today["balance"]
                    else:
                        daily_total = last_transaction_today.balance
                else:
                    daily_total = account["previous_balance"]
                current_balance = daily_total
                account["previous_balance"] = daily_total
                account["data"].append(current_balance)
                today_total += current_balance
            totals.append(today_total)

        # Prepare the graph data for the forecast object
        datasets_out = DatasetObject(
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
        datasets.append(datasets_out)
        for index, account in enumerate(account_info):
            datasets_out = DatasetObject(
                borderColor=colors[index],
                backgroundColor=colors[index],
                tension=0.1,
                data=account["data"],
                pointStyle="line",
                radius=2,
                hitRadius=5,
                hoverRadius=5,
                label=account["name"],
            )
            datasets.append(datasets_out)
        forecast_out = ForecastOut(labels=labels, datasets=datasets)
        logToDB(
            "Forecast retrieved",
            None,
            None,
            None,
            3002002,
            1,
        )
        return forecast_out
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Forecast not retrieved : {str(e)}",
            None,
            None,
            None,
            3002902,
            2,
        )
        raise HttpError(500, f"Record retrieval error : {str(e)}")
