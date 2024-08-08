from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from administration.models import Option
from tags.models import Tag
from transactions.models import Transaction, TransactionDetail
from tags.api.schemas.graph_by_tags import GraphDataset, GraphOut
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
import json
from django.utils import timezone
import pytz
import os
from dateutil.relativedelta import relativedelta
import random

graph_by_tags_router = Router(tags=["Graph By Tags"])


@graph_by_tags_router.get("/get", response=GraphOut)
def get_graph(request, widget_id: int):
    """
    The function `get_graph` retrieves graph data for tags for widget id.

    Args:
        request (HttpRequest): The HTTP request object.
        widget_id (int): The widget for graph data

    Returns:
        GraphOut: the graph data object
    """

    try:
        # Initialize variables
        graph_name = ""
        exclude = "[0]"
        tagID = None
        month = 0
        expense = True
        tags = None

        # Load the options for the specified widget ID
        options = get_object_or_404(Option, id=1)

        # Set graph options based on widget options
        if widget_id == 1:
            graph_name = options.widget1_graph_name
            exclude = options.widget1_exclude
            tagID = options.widget1_tag_id
            month = options.widget1_month
            expense = options.widget1_expense
        if widget_id == 2:
            graph_name = options.widget2_graph_name
            exclude = options.widget2_exclude
            tagID = options.widget2_tag_id
            month = options.widget2_month
            expense = options.widget2_expense
        if widget_id == 3:
            graph_name = options.widget3_graph_name
            exclude = options.widget3_exclude
            tagID = options.widget3_tag_id
            month = options.widget3_month
            expense = options.widget3_expense
        exclude_list = json.loads(exclude)
        today = timezone.now()
        tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
        today_tz = today.astimezone(tz_timezone).date()
        target_date = today_tz - relativedelta(months=month)
        target_month = target_date.month
        target_year = target_date.year
        labels = []
        values = []
        datasets = []
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

        # Sort colors randomly, seeded to stay the same for this month
        random.seed(today_tz.month * widget_id)
        random.shuffle(colors)

        # If a tag is specified in options, filter by that tag
        # Otherwise, filter on expense tags or income tags
        if tagID is None:
            tag_type_id = 1 if expense else 2
            tags = (
                Tag.objects.filter(tag_type__id=tag_type_id)
                .exclude(id__in=exclude_list)
                .exclude(child__isnull=False)
            )
            # Calculate month totals for each tag
            # Use the tag name as the label and the total as the value
            for tag in tags:
                tag_amount = (
                    TransactionDetail.objects.filter(
                        tag__parent=tag.parent,
                        transaction__transaction_date__month=target_month,
                        transaction__transaction_date__year=target_year,
                        transaction__status__id__gt=1,
                    ).aggregate(Sum("detail_amt"))["detail_amt__sum"]
                    or 0
                )
                if tag_amount != 0:
                    labels.append(tag.tag_name)
                    values.append(tag_amount)
            result = Transaction.objects.filter(
                transaction_date__month=target_month,
                transaction_date__year=target_year,
                status__id__gt=1,
                transaction_type_id=tag_type_id,
            )
            result = result.annotate(tag_count=Count("transactiondetail__id"))
            result = result.filter(tag_count=0)

            result = result.aggregate(total=Sum(F("total_amount")))

            untagged_total = result["total"] or 0
            if untagged_total != 0:
                values.append(untagged_total)
                labels.append("Untagged")
        elif tagID != -1:
            tags = Tag.objects.filter(parent__id=tagID).exclude(
                id__in=exclude_list
            )

            # Calculate month totals for each tag
            # Use the tag name as the label and the total as the value
            for tag in tags:
                tag_amount = (
                    TransactionDetail.objects.filter(
                        tag=tag,
                        transaction__transaction_date__month=target_month,
                        transaction__transaction_date__year=target_year,
                        transaction__status__id__gt=1,
                    ).aggregate(Sum("detail_amt"))["detail_amt__sum"]
                    or 0
                )
                if tag_amount != 0:
                    labels.append(tag.child.tag_name)
                    values.append(tag_amount)
        elif tagID == -1:
            result = Transaction.objects.filter(
                transaction_date__month=target_month,
                transaction_date__year=target_year,
                status__id__gt=1,
            )
            result = result.annotate(tag_count=Count("transactiondetail__id"))
            result = result.filter(tag_count=0)

            result = result.aggregate(total=Sum(F("total_amount")))

            untagged_total = result["total"] or 0
            values.append(untagged_total)
            labels.append("Untagged")

        # If there are no tags or totals, return None as label and 0 as value
        if not values:
            values.append(0)
        if not labels:
            labels.append("None")

        # Prepare the graph data object
        dataset = GraphDataset(
            label=graph_name, data=values, backgroundColor=colors, hoverOffset=4
        )
        datasets.append(dataset)
        graph_object = GraphOut(labels=labels, datasets=datasets)
        logToDB(
            f"Graph data retrieved : {widget_id}",
            None,
            None,
            None,
            3002003,
            1,
        )
        return graph_object
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Graph data not retrieved : {str(e)}",
            None,
            None,
            None,
            3002903,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")
