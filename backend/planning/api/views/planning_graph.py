from ninja import Router
from ninja.errors import HttpError
from planning.api.schemas.planning_graph import (
    PlanningGraphList,
    PlanningGraphOut,
)
from administration.api.dependencies.log_to_db import logToDB
from django.shortcuts import get_object_or_404
from typing import List
from django.db.models import (
    Case,
    When,
    Q,
    Value,
    CharField,
    Sum,
    FloatField,
)
from django.db.models.functions import Coalesce
import pytz
import os
from django.utils import timezone
from accounts.api.schemas.forecast import DatasetObject, GraphData
from administration.models import Option
from transactions.models import Paycheck
from tags.models import Tag
import json

planning_graph_router = Router(tags=["Planning Graphs"])


@planning_graph_router.get("/list", response=List[PlanningGraphList])
def list_graph_totals(request, graph_type: str):
    """
    The function `list_graph_totals` retrieves transactions for pay or expenses,
    and calcualtes the totals by month for the current year and last year, as
    well as the averages by month for the years and returns the data as graph
    data.

    Args:
        request (HttpRequest): The HTTP request object.
        graph_type (str): Either pay or expense.

    Returns:
        PlanningGraphOut: the planning graph object
    """
    try:
        # Calculate dates based on month, year
        today = timezone.now()
        tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
        today_tz = today.astimezone(tz_timezone).date()
        this_month = today_tz.month
        this_year = today_tz.year
        last_year = today_tz.year - 1
        all_reports = []

        # If expenses
        if graph_type == "expense":
            try:
                options = get_object_or_404(Option, id=1)
                report_main = json.loads(options.report_main)
                report_individual = json.loads(options.report_individual)
                # Retrieve main report transactions
                title = "Main"
                sub_graph_data = []
                for tag in report_main:
                    tag_detail = Tag.objects.get(
                        parent_id=tag, child__isnull=True
                    )
                    pretty_name = tag_detail.parent.tag_name
                    tag_group_totals = Tag.objects.filter(
                        parent_id=tag
                    ).annotate(
                        total_this_year=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_last_year=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_jan_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=1
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_feb_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=2
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_mar_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=3
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_apr_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=4
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_may_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=5
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_jun_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=6
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_jul_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=7
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_aug_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=8
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_sep_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=9
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_oct_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=10
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_nov_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=11
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_dec_current=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=12
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=this_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_jan_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=1
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_feb_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=2
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_mar_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=3
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_apr_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=4
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_may_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=5
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_jun_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=6
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_jul_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=7
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_aug_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=8
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_sep_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=9
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_oct_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=10
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_nov_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=11
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        total_dec_last=Coalesce(
                            Sum(
                                "transactiondetail__detail_amt",
                                filter=Q(
                                    transactiondetail__transaction__transaction_date__month=12
                                )
                                & Q(
                                    transactiondetail__transaction__transaction_date__year=last_year
                                ),
                                output_field=FloatField(),
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                    )

                    # Calculate averages
                    current_avg = abs(
                        sum(item.total_this_year for item in tag_group_totals)
                        / this_month
                    )
                    last_avg = abs(
                        sum(item.total_last_year for item in tag_group_totals)
                        / 12
                    )

                    this_year_data = [
                        abs(
                            sum(
                                item.total_jan_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_feb_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_mar_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_apr_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_may_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_jun_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_jul_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_aug_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_sep_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_oct_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_nov_current
                                for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_dec_current
                                for item in tag_group_totals
                            )
                        ),
                        current_avg,
                    ]
                    last_year_data = [
                        abs(
                            sum(
                                item.total_jan_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_feb_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_mar_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_apr_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_may_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_jun_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_jul_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_aug_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_sep_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_oct_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_nov_last for item in tag_group_totals
                            )
                        ),
                        abs(
                            sum(
                                item.total_dec_last for item in tag_group_totals
                            )
                        ),
                        last_avg,
                    ]
                    planning_graph_out = prepare_planning_graph(
                        pretty_name,
                        this_year_data,
                        last_year_data,
                        this_year,
                        last_year,
                    )
                    sub_graph_data.append(planning_graph_out)
                graph_object = PlanningGraphList(
                    title=title, data=sub_graph_data
                )
                all_reports.append(graph_object)

                # Retrieve individual report transactions
                for tag in report_individual:
                    sub_graph_data = []
                    tag_detail = Tag.objects.get(
                        parent_id=tag, child__isnull=True
                    )
                    title = tag_detail.parent.tag_name
                    sub_tags = Tag.objects.filter(
                        parent__id=tag, child__isnull=False
                    )
                    transactions_by_tag = sub_tags.annotate(
                        total_this_year=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_last_year=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_jan_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=1,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_feb_current=Sum(
                            Case(
                                When(
                                    transactiondetail__transaction__transaction_date__year=this_year,
                                    transactiondetail__transaction__transaction_date__month=2,
                                    then="transactiondetail__detail_amt",
                                ),
                                default=0.0,
                                output_field=FloatField(),
                            )
                        ),
                        total_mar_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=3,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_apr_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=4,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_may_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=5,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_jun_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=6,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_jul_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=7,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_aug_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=8,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_sep_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=9,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_oct_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=10,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_nov_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=11,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_dec_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        transactiondetail__transaction__transaction_date__month=12,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_jan_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=1,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_feb_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=2,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_mar_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=3,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_apr_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=4,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_may_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=5,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_jun_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=6,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_jul_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=7,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_aug_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=8,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_sep_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=9,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_oct_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=10,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_nov_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=11,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        total_dec_last=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        transactiondetail__transaction__transaction_date__month=12,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                        ),
                        last_year_avg=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=last_year,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            )
                            / 12,
                            Value(0.0),
                        ),
                        current_year_avg=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transactiondetail__transaction__transaction_date__year=this_year,
                                        then="transactiondetail__detail_amt",
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            )
                            / this_month,
                            Value(0.0),
                        ),
                        pretty_name=Case(
                            When(
                                child__isnull=False,
                                then="child__tag_name",
                            ),
                            When(
                                child__isnull=True,
                                then="parent__tag_name",
                            ),
                            output_field=CharField(),
                        ),
                    )
                    for sub_tag in transactions_by_tag:
                        pretty_name = sub_tag.pretty_name
                        this_year_data = [
                            abs(sub_tag.total_jan_current),
                            abs(sub_tag.total_feb_current),
                            abs(sub_tag.total_mar_current),
                            abs(sub_tag.total_apr_current),
                            abs(sub_tag.total_may_current),
                            abs(sub_tag.total_jun_current),
                            abs(sub_tag.total_jul_current),
                            abs(sub_tag.total_aug_current),
                            abs(sub_tag.total_sep_current),
                            abs(sub_tag.total_oct_current),
                            abs(sub_tag.total_nov_current),
                            abs(sub_tag.total_dec_current),
                            abs(sub_tag.current_year_avg),
                        ]
                        last_year_data = [
                            abs(sub_tag.total_jan_last),
                            abs(sub_tag.total_feb_last),
                            abs(sub_tag.total_mar_last),
                            abs(sub_tag.total_apr_last),
                            abs(sub_tag.total_may_last),
                            abs(sub_tag.total_jun_last),
                            abs(sub_tag.total_jul_last),
                            abs(sub_tag.total_aug_last),
                            abs(sub_tag.total_sep_last),
                            abs(sub_tag.total_oct_last),
                            abs(sub_tag.total_nov_last),
                            abs(sub_tag.total_dec_last),
                            abs(sub_tag.last_year_avg),
                        ]

                        planning_graph_out = prepare_planning_graph(
                            pretty_name,
                            this_year_data,
                            last_year_data,
                            this_year,
                            last_year,
                        )
                        sub_graph_data.append(planning_graph_out)
                    graph_object = PlanningGraphList(
                        title=title, data=sub_graph_data
                    )
                    all_reports.append(graph_object)
                logToDB(
                    f"{graph_type} graph details retrieved",
                    None,
                    None,
                    None,
                    3002004,
                    0,
                )
            except Exception as e:
                # Log other types of exceptions
                logToDB(
                    f"{graph_type} graph details not retrieved : {str(e)}",
                    None,
                    None,
                    None,
                    3002904,
                    2,
                )
                raise HttpError(
                    500, f"{graph_type} graph details retrieval error: {str(e)}"
                )
        elif graph_type == "pay":
            try:
                sub_graph_data = []
                paychecks = Paycheck.objects.filter(
                    transaction__transaction_date__year__gte=last_year
                )
                fields = [
                    "gross",
                    "net",
                    "taxes",
                    "health",
                    "pension",
                    "fsa",
                    "dca",
                    "union_dues",
                    "four_fifty_seven_b",
                ]
                fields_pretty = [
                    "Gross",
                    "Net",
                    "Taxes",
                    "Health",
                    "Pension",
                    "FSA",
                    "DCA",
                    "Union Dues",
                    "457B",
                ]
                for i, field in enumerate(fields):
                    totals_this_year = paychecks.filter(
                        transaction__transaction_date__year=this_year
                    ).aggregate(
                        jan_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=1,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        feb_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=2,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        mar_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=3,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        apr_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=4,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        may_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=5,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        jun_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=6,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        jul_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=7,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        aug_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=8,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        sep_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=9,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        oct_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=10,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        nov_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=11,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        dec_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=12,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        year_total=Coalesce(
                            Sum(field), Value(0.0), output_field=FloatField()
                        ),
                    )
                    totals_last_year = paychecks.filter(
                        transaction__transaction_date__year=last_year
                    ).aggregate(
                        jan_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=1,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        feb_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=2,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        mar_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=3,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        apr_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=4,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        may_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=5,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        jun_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=6,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        jul_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=7,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        aug_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=8,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        sep_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=9,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        oct_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=10,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        nov_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=11,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        dec_total=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__month=12,
                                        then=field,
                                    ),
                                    default=0.0,
                                    output_field=FloatField(),
                                )
                            ),
                            Value(0.0),
                            output_field=FloatField(),
                        ),
                        year_total=Coalesce(
                            Sum(field), Value(0.0), output_field=FloatField()
                        ),
                    )
                    this_year_avg = totals_this_year["year_total"] / this_month
                    last_year_avg = totals_last_year["year_total"] / 12
                    this_year_data = [
                        totals_this_year["jan_total"],
                        totals_this_year["feb_total"],
                        totals_this_year["mar_total"],
                        totals_this_year["apr_total"],
                        totals_this_year["may_total"],
                        totals_this_year["jun_total"],
                        totals_this_year["jul_total"],
                        totals_this_year["aug_total"],
                        totals_this_year["sep_total"],
                        totals_this_year["oct_total"],
                        totals_this_year["nov_total"],
                        totals_this_year["dec_total"],
                        this_year_avg,
                    ]
                    last_year_data = [
                        totals_last_year["jan_total"],
                        totals_last_year["feb_total"],
                        totals_last_year["mar_total"],
                        totals_last_year["apr_total"],
                        totals_last_year["may_total"],
                        totals_last_year["jun_total"],
                        totals_last_year["jul_total"],
                        totals_last_year["aug_total"],
                        totals_last_year["sep_total"],
                        totals_last_year["oct_total"],
                        totals_last_year["nov_total"],
                        totals_last_year["dec_total"],
                        last_year_avg,
                    ]
                    graph_data = prepare_planning_graph(
                        fields_pretty[i],
                        this_year_data,
                        last_year_data,
                        this_year,
                        last_year,
                    )
                    sub_graph_data.append(graph_data)
                graph_object = PlanningGraphList(
                    title="Pay", data=sub_graph_data
                )
                all_reports.append(graph_object)
                logToDB(
                    f"{graph_type} graph details retrieved",
                    None,
                    None,
                    None,
                    3002004,
                    0,
                )
            except Exception as e:
                # Log other types of exceptions
                logToDB(
                    f"{graph_type} graph details not retrieved(Pay) : {str(e)}",
                    None,
                    None,
                    None,
                    3002904,
                    2,
                )
                raise HttpError(
                    500,
                    f"{graph_type} graph details retrieval error(Pay): {str(e)}",
                )
        logToDB(
            f"{graph_type} planning graph retrieved",
            None,
            None,
            None,
            3002004,
            0,
        )
        return all_reports
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"{graph_type} planning graph not retrieved : {str(e)}",
            None,
            None,
            None,
            3002904,
            2,
        )
        raise HttpError(
            500, f"{graph_type} planning graph retrieval error: {str(e)}"
        )


def prepare_planning_graph(
    pretty_name: str,
    this_year_data: List[float],
    last_year_data: List[float],
    this_year: int,
    last_year: int,
):
    """
    The function `prepare_planning_graph` sets up a planning graph
    object based on supplied data for current and last year.

    Args:
        pretty_name (str): The HTTP request object.
        this_year_data (List[float]): A list of totals for this year
        last_year_data (List[float]): A list of totals for last year
        this_year (int): The 4 digit year for this year
        last_year (int): The 4 digit year for last year

    Returns:
        planning_graph_out (PlanningGraphOut): the planning graph object
    """
    try:
        key_name = pretty_name.replace(" ", "_").lower()
        this_year_monthly_data = []
        last_year_monthly_data = []
        for i in range(0, 12):
            this_year_monthly_data.append(round(abs(this_year_data[i]), 2))
            last_year_monthly_data.append(round(abs(last_year_data[i]), 2))

        # Prepare the datasets
        datasets = []
        this_year_dataset = DatasetObject(
            label=f"{this_year}",
            backgroundColor="#046959",
            data=this_year_monthly_data,
        )
        datasets.append(this_year_dataset)
        last_year_dataset = DatasetObject(
            label=f"{last_year}",
            backgroundColor="#c2fff5",
            data=last_year_monthly_data,
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

        # Prepare the planning graph out object
        planning_graph_out = PlanningGraphOut(
            data=graph_data,
            year1=this_year,
            year2=last_year,
            year1_avg=round(this_year_data[12], 2),
            year2_avg=round(last_year_data[12], 2),
            pretty_name=pretty_name,
            key_name=key_name,
        )
        logToDB(
            f"Planning graph prepared({pretty_name})",
            None,
            None,
            None,
            3002004,
            0,
        )
        return planning_graph_out
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Planning graph not prepared({pretty_name}) : {str(e)}",
            None,
            None,
            None,
            3002904,
            2,
        )
        raise HttpError(500, f"Planning graph preperation error: {str(e)}")
