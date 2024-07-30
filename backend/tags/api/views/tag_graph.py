from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from accounts.models import Account
from transactions.models import TransactionDetail
from tags.api.schemas.tag_graph import TagGraphOut
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
import pytz
import os
from django.utils import timezone
from accounts.api.schemas.forecast import DatasetObject, GraphData

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
        source_account_name = Account.objects.filter(
            id=OuterRef("transaction__source_account_id")
        ).values("account_name")[:1]
        destination_account_name = Account.objects.filter(
            id=OuterRef("transaction__destination_account_id")
        ).values("account_name")[:1]

        # Retrieve all transactions for tag
        alltrans = TransactionDetail.objects.filter(
            Q(tag__id=tag) & Q(transaction__status__id__gt=1)
        ).order_by("-transaction__transaction_date")

        # Annotate source account names
        alltrans = alltrans.annotate(
            source_name=Coalesce(
                Subquery(source_account_name), Value("Unknown Account")
            )
        )

        # Annotate destination account names
        alltrans = alltrans.annotate(
            destination_name=Coalesce(
                Subquery(destination_account_name), Value("Unknown Account")
            )
        )

        # Annotate pretty account
        alltrans = alltrans.annotate(
            pretty_account=Case(
                When(
                    transaction__transaction_type_id=3,
                    then=Concat(
                        F("source_name"),
                        Value(" => "),
                        F("destination_name"),
                    ),
                ),
                default=F("source_name"),
                output_field=CharField(),  # Correctly specify the output field
            )
        )

        # Filter transactions for current year
        thisyear_trans = alltrans.filter(
            transaction__transaction_date__year=this_year
        ).order_by("-transaction__transaction_date")

        # Filter transactions for last year
        lastyear_trans = alltrans.filter(
            transaction__transaction_date__year=last_year
        ).order_by("-transaction__transaction_date")

        # Calculate the YTD total
        this_year_total = 0
        this_year_total = thisyear_trans.aggregate(
            total_amount=Sum("detail_amt")
        )["total_amount"]
        if this_year_total is not None:
            this_year_total = abs(this_year_total)
        else:
            this_year_total = 0

        # Calculate last years total
        last_year_total = 0
        last_year_total = lastyear_trans.aggregate(
            total_amount=Sum("detail_amt")
        )["total_amount"]
        if last_year_total is not None:
            last_year_total = abs(last_year_total)
        else:
            last_year_total = 0

        # Calculate YTD Monthly average
        if this_year_total is not None:
            this_year_avg = this_year_total / this_month
        else:
            this_year_avg = 0
        this_year_avg = round(this_year_avg, 2)
        # Calculate Last Year Monthly average
        if last_year_total is not None:
            last_year_avg = last_year_total / 12
        else:
            last_year_avg = 0
        last_year_avg = round(last_year_avg, 2)

        # Calculate this year monthly totals
        this_year_totals = []
        for month in range(1, this_month + 1):
            monthly_total = 0
            monthly_total = thisyear_trans.filter(
                transaction__transaction_date__month=month
            ).aggregate(monthly_total=Sum("detail_amt"))["monthly_total"]
            if monthly_total is not None:
                this_year_totals.append(abs(monthly_total))
            else:
                this_year_totals.append(0)

        # Calculate last year monthly totals
        last_year_totals = []
        for month in range(1, 13):
            monthly_total = 0
            monthly_total = lastyear_trans.filter(
                transaction__transaction_date__month=month
            ).aggregate(monthly_total=Sum("detail_amt"))["monthly_total"]
            if monthly_total is not None:
                last_year_totals.append(abs(monthly_total))
            else:
                last_year_totals.append(0)

        # Prepare the datasets
        datasets = []
        this_year_dataset = DatasetObject(
            label=this_year, backgroundColor="#046959", data=this_year_totals
        )
        datasets.append(this_year_dataset)
        last_year_dataset = DatasetObject(
            label=last_year, backgroundColor="#c2fff5", data=last_year_totals
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
            transactions=list(alltrans),
        )
        logToDB(
            f"Tag details retrieved : {tag}",
            None,
            None,
            None,
            3002004,
            1,
        )
        return tag_graph_out
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Tag details not retrieved : {str(e)}",
            None,
            None,
            None,
            3002904,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")
