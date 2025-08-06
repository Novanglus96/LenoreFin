from ninja import Router
from ninja.errors import HttpError
from accounts.api.schemas.forecast import (
    TargetObject,
    FillObject,
    DatasetObject,
    ForecastOut,
)
from administration.api.dependencies.log_to_db import logToDB
from accounts.api.dependencies.get_dates_in_range import get_dates_in_range
from accounts.api.dependencies.get_forecast_end_date import (
    get_forecast_end_date,
)
from accounts.api.dependencies.get_forecast_start_date import (
    get_forecast_start_date,
)
from transactions.api.dependencies.get_complete_transaction_list_with_totals import (
    get_complete_transaction_list_with_totals,
)
from datetime import datetime

forecast_router = Router(tags=["Account Forecasts"])


@forecast_router.get("/get/{account_id}", response=ForecastOut)
def get_forecast(
    request, account_id: int, start_interval: int, end_interval: int
):
    """
    The function `get_forecast` retrieves the forecast data for the account id

    Args:
        request (HttpRequest): The HTTP request object.
        account_id (int): The id of the account to retrieve forecast data.
        start_interval (int): the number of days before today to start forecast.
        end_interval (int): the number of days after today to end forecast.

    Returns:
        ForecastOut: the forecast object

    Raises:
        Http404: If the account with the specified ID does not exist.
    """

    try:
        # Retrieve the dates in range as labels for forecast
        labels = get_dates_in_range(start_interval, end_interval)

        data = []
        datasets = []

        # Retrieve the transactions in the date range for the account
        start_date = get_forecast_start_date(start_interval)
        end_date = get_forecast_end_date(end_interval)

        # Get list of transactions
        transactions_list, previous_balance = (
            get_complete_transaction_list_with_totals(
                end_date, account_id, True, True, start_date
            )
        )

        # Get the initial balance
        # Use opening balance or first previous balance available
        daily_total = 0

        # Get the totals by day
        for label_date in labels:
            parsed_date = datetime.strptime(label_date, "%b %d, %y")
            formatted_date = parsed_date.strftime("%Y-%m-%d")
            transactions_today = []
            for transaction in transactions_list:
                if isinstance(transaction, dict):
                    if str(transaction["transaction_date"]) == str(
                        formatted_date
                    ):
                        transactions_today.append(transaction)
                else:
                    if str(transaction.transaction_date) == str(formatted_date):
                        transactions_today.append(transaction)
            if len(transactions_today) > 0:
                last_transaction_today = transactions_today[-1]
                if isinstance(last_transaction_today, dict):
                    daily_total = last_transaction_today["balance"]
                else:
                    daily_total = last_transaction_today.balance
            else:
                daily_total = previous_balance
            current_balance = daily_total
            previous_balance = daily_total
            data.append(current_balance)

        # Prepare the graph data for the forecast object
        targetobject_out = TargetObject(value=0)
        fillobject_out = FillObject(
            target=targetobject_out,
            above="rgb(236 , 253, 245)",
            below="rgb(248, 121, 121)",
        )
        datasets_out = DatasetObject(
            borderColor="#06966A",
            backgroundColor="#06966A",
            tension=0.1,
            data=data,
            fill=fillobject_out,
            pointStyle="circle",
            radius=2,
            hitRadius=5,
            hoverRadius=5,
        )
        datasets.append(datasets_out)
        forecast_out = ForecastOut(labels=labels, datasets=datasets)
        logToDB(
            "Forecast retrieved",
            account_id,
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
            account_id,
            None,
            None,
            3002902,
            2,
        )
        raise HttpError(500, f"Record retrieval error : {str(e)}")
