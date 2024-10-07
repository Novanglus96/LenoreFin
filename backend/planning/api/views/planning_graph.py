from ninja import Router, Query
from django.db import IntegrityError
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
from administration.models import Option
from transactions.models import Transaction, TransactionDetail
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
            alltrans = TransactionDetail.objects.filter(
                transaction__transaction_date__year__gte=last_year,
                transaction__status__id__gt=1,
            ).order_by("-transaction__transaction_date")
            options = get_object_or_404(Option, id=1)
            report_main = json.loads(options.report_main)
            report_individual = json.loads(options.report_individual)
            # Retrieve main transactions
            for tag in report_main:
                sub_graph_data = []
                tag_detail = Tag.objects.get(parent_id=tag, child__isnull=True)
                print(f"tag_detail: {tag_detail}")
                title = tag_detail.parent.tag_name
                sub_tags = Tag.objects.filter(parent__id=tag)
                transactions_by_tag = (
                    alltrans.filter(tag__in=sub_tags)
                    .values("tag")
                    .annotate(
                        total_this_year=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__year=this_year,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=1,
                                        then="detail_amt",
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
                                    transaction__transaction_date__year=this_year,
                                    transaction__transaction_date__month=2,
                                    then="detail_amt",
                                ),
                                default=0.0,
                                output_field=FloatField(),
                            )
                        ),
                        total_mar_current=Coalesce(
                            Sum(
                                Case(
                                    When(
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=3,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=4,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=5,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=6,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=7,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=8,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=9,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=10,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=11,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        transaction__transaction_date__month=12,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=1,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=2,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=3,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=4,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=5,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=6,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=7,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=8,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=9,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=10,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=11,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        transaction__transaction_date__month=12,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=last_year,
                                        then="detail_amt",
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
                                        transaction__transaction_date__year=this_year,
                                        then="detail_amt",
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
                                tag__child__isnull=False,
                                then="tag__child__tag_name",
                            ),
                            When(
                                tag__child__isnull=True,
                                then="tag__parent__tag_name",
                            ),
                            output_field=CharField(),
                        ),
                    )
                )
                print(f"transactions_by_tag: {transactions_by_tag}")
                for sub_tag in transactions_by_tag:
                    pretty_name = sub_tag["pretty_name"]
                    key_name = pretty_name.replace(" ", "_").lower()

                    # Prepare the datasets
                    datasets = []
                    this_year_dataset = DatasetObject(
                        label=this_year,
                        backgroundColor="#046959",
                        data=[
                            sub_tag["total_jan_current"],
                            sub_tag["total_feb_current"],
                            sub_tag["total_mar_current"],
                            sub_tag["total_apr_current"],
                            sub_tag["total_may_current"],
                            sub_tag["total_jun_current"],
                            sub_tag["total_jul_current"],
                            sub_tag["total_aug_current"],
                            sub_tag["total_sep_current"],
                            sub_tag["total_oct_current"],
                            sub_tag["total_nov_current"],
                            sub_tag["total_dec_current"],
                        ],
                    )
                    datasets.append(this_year_dataset)
                    last_year_dataset = DatasetObject(
                        label=last_year,
                        backgroundColor="#c2fff5",
                        data=[
                            sub_tag["total_jan_last"],
                            sub_tag["total_feb_last"],
                            sub_tag["total_mar_last"],
                            sub_tag["total_apr_last"],
                            sub_tag["total_may_last"],
                            sub_tag["total_jun_last"],
                            sub_tag["total_jul_last"],
                            sub_tag["total_aug_last"],
                            sub_tag["total_sep_last"],
                            sub_tag["total_oct_last"],
                            sub_tag["total_nov_last"],
                            sub_tag["total_dec_last"],
                        ],
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
                    tag_graph_out = PlanningGraphOut(
                        data=graph_data,
                        year1=this_year,
                        year2=last_year,
                        year1_avg=sub_tag["current_year_avg"],
                        year2_avg=sub_tag["last_year_avg"],
                        pretty_name=pretty_name,
                        key_name=key_name,
                    )
                    sub_graph_data.append(tag_graph_out)
                graph_object = PlanningGraphList(
                    title=title, data=sub_graph_data
                )
            all_reports.append(graph_object)
        return all_reports
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
