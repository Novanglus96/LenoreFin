from ninja import Router
from ninja.errors import HttpError
from transactions.models import TransactionDetail
from tags.api.schemas.tag_graph import TagGraphOut
import pytz
import os
from django.utils import timezone
from accounts.api.schemas.forecast import DatasetObject, GraphData
from transactions.api.dependencies.get_transactions_by_tag import (
    get_transactions_by_tag,
)
from datetime import date
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

tag_graph_router = Router(tags=["Tag Graphs"])


@tag_graph_router.get("/list", response=TagGraphOut)
def list_transactions_bytag(request, tag: int):
    """
    The function `list_transactions_bytag` retrieves transactions for a tag id,
    and calcualtes the totals by month for the current year and last year, as
    well as the averages by month for the years and returns the data as graph
    data.

    Args:
        request (HttpRequest): The HTTP request object.
        tag (int): The tag id to get transactions for.
        month (int): Optional month integer.  If none is provided, 0

    Returns:
        TagDetailOut: the tag detail object
    """

    try:
        # Calculate dates based on month, year
        today = timezone.now()
        tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
        today_tz = today.astimezone(tz_timezone).date()
        this_month = today_tz.month
        this_year = today_tz.year
        last_year = today_tz.year - 1
        first_day_last_year = date(last_year, 1, 1)

        # Get transactions
        tags = [tag]
        tag_transactions = get_transactions_by_tag(
            today_tz, False, first_day_last_year, tags, True
        )

        # Loop through transactions
        current_year_total = 0
        previous_year_total = 0
        last_year_monthly_totals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        this_year_monthly_totals = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for transaction in tag_transactions:
            transaction_detail = TransactionDetail.objects.get(
                transaction__id=transaction.id, tag__id=tag
            )
            if transaction.transaction_date.year == this_year:
                current_year_total += abs(transaction_detail.detail_amt)
                this_year_monthly_totals[
                    transaction.transaction_date.month - 1
                ] += abs(transaction_detail.detail_amt)
            elif transaction.transaction_date.year == last_year:
                previous_year_total += abs(transaction_detail.detail_amt)
                last_year_monthly_totals[
                    transaction.transaction_date.month - 1
                ] += abs(transaction_detail.detail_amt)
            transaction.balance = transaction_detail.detail_amt

        # Calculate YTD Monthly average
        if current_year_total is not None:
            this_year_avg = current_year_total / this_month
        else:
            this_year_avg = 0
        this_year_avg = round(this_year_avg, 2)

        # Calculate Last Year Monthly average
        if previous_year_total is not None:
            last_year_avg = previous_year_total / 12
        else:
            last_year_avg = 0
        last_year_avg = round(last_year_avg, 2)

        # Prepare the datasets
        datasets = []
        this_year_dataset = DatasetObject(
            label=f"{this_year}",
            backgroundColor="#046959",
            data=this_year_monthly_totals,
        )
        datasets.append(this_year_dataset)
        last_year_dataset = DatasetObject(
            label=f"{last_year}",
            backgroundColor="#c2fff5",
            data=last_year_monthly_totals,
        )
        datasets.append(last_year_dataset)

        # Prepare the GraphData object
        graph_data = GraphData(
            labels=[
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
            datasets=datasets,
        )

        # Prepare the tag graph out object
        tag_graph_out = TagGraphOut(
            data=graph_data,
            year1=this_year,
            year2=last_year,
            year1_avg=this_year_avg,
            year2_avg=last_year_avg,
            transactions=tag_transactions,
        )
        api_logger.debug(f"Tag details retrieved : {tag}")
        return tag_graph_out
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Tag details not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")
