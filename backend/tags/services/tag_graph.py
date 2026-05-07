import json
import os
import random
from typing import List, Tuple

import pytz
from dateutil.relativedelta import relativedelta
from django.db.models import Count, F, Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from administration.models import Option
from tags.api.schemas.graph_by_tags import GraphDataset, GraphOut, PieGraphItem
from tags.models import Tag
from transactions.models import Transaction, TransactionDetail

import logging

service_logger = logging.getLogger("api")
error_logger = logging.getLogger("error")

GRAPH_COLORS = [
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


def _resolve_widget_options(options: Option, widget_id: int) -> dict:
    """Extract the relevant widget settings from the Options object."""
    if widget_id == 1:
        return {
            "graph_name": options.widget1_graph_name,
            "exclude": options.widget1_exclude,
            "tag_id": options.widget1_tag_id,
            "month": options.widget1_month,
            "type_id": options.widget1_type_id,
        }
    if widget_id == 2:
        return {
            "graph_name": options.widget2_graph_name,
            "exclude": options.widget2_exclude,
            "tag_id": options.widget2_tag_id,
            "month": options.widget2_month,
            "type_id": options.widget2_type_id,
        }
    if widget_id == 3:
        return {
            "graph_name": options.widget3_graph_name,
            "exclude": options.widget3_exclude,
            "tag_id": options.widget3_tag_id,
            "month": options.widget3_month,
            "type_id": options.widget3_type_id,
        }
    return {
        "graph_name": "",
        "exclude": "[0]",
        "tag_id": None,
        "month": 0,
        "type_id": 0,
    }


def _get_tags_and_result(
    type_id: int, tag_id, exclude_list: list, target_month: int, target_year: int
) -> Tuple:
    """Return (tags queryset, result queryset) for the given type_id."""
    tags = None
    result = None

    if type_id == 1:
        tags = (
            Tag.objects.filter(tag_type__id=1)
            .exclude(id__in=exclude_list)
            .exclude(child__isnull=False)
        )
        result = Transaction.objects.filter(
            transaction_date__month=target_month,
            transaction_date__year=target_year,
            transaction_type_id=1,
        )
    elif type_id == 2:
        tags = (
            Tag.objects.filter(tag_type__id=2)
            .exclude(id__in=exclude_list)
            .exclude(child__isnull=False)
        )
        result = Transaction.objects.filter(
            transaction_date__month=target_month,
            transaction_date__year=target_year,
            transaction_type_id=2,
        )
    elif type_id == 3:
        tags = []
        result = Transaction.objects.filter(
            transaction_date__month=target_month,
            transaction_date__year=target_year,
        )
    elif type_id == 4:
        tags = Tag.objects.filter(parent__id=tag_id).exclude(id__in=exclude_list)

    return tags, result


def _accumulate_labels_and_values(
    tags, type_id: int, target_month: int, target_year: int
) -> Tuple[list, list]:
    """Walk the tag queryset and build parallel labels/values lists."""
    labels = []
    values = []

    for tag in tags:
        tag_amount = 0
        if type_id != 4:
            tag_amount = (
                TransactionDetail.objects.filter(
                    tag__parent=tag.parent,
                    transaction__transaction_date__month=target_month,
                    transaction__transaction_date__year=target_year,
                ).aggregate(Sum("detail_amt"))["detail_amt__sum"]
                or 0
            )
            if tag_amount != 0:
                labels.append(tag.tag_name)
                values.append(tag_amount)
        else:
            tag_amount = (
                TransactionDetail.objects.filter(
                    tag=tag,
                    transaction__transaction_date__month=target_month,
                    transaction__transaction_date__year=target_year,
                ).aggregate(Sum("detail_amt"))["detail_amt__sum"]
                or 0
            )
            if tag_amount != 0:
                if tag.child:
                    labels.append(tag.child.tag_name)
                else:
                    labels.append(tag.parent.tag_name)
                values.append(tag_amount)

    return labels, values


def _append_untagged(result, values: list, labels: list) -> None:
    """Annotate untagged transactions and add them to values/labels in-place."""
    if result:
        annotated = result.annotate(tag_count=Count("transactiondetail__id"))
        annotated = annotated.filter(tag_count=0)
        agg = annotated.aggregate(total=Sum(F("total_amount")))
        untagged_total = agg["total"] or 0
        if untagged_total != 0:
            values.append(untagged_total)
            labels.append("Untagged")


def _sort_and_cap(
    values: list, labels: list
) -> Tuple[list, list]:
    """Sort by absolute value descending and cap at 10 items."""
    if not values:
        values.append(0)
    if not labels:
        labels.append("None")

    paired = sorted(zip(values, labels), key=lambda x: abs(x[0]), reverse=True)
    sorted_values, sorted_labels = zip(*paired)
    sorted_values = list(sorted_values)
    sorted_labels = list(sorted_labels)

    if len(sorted_values) > 10:
        remaining = sum(sorted_values[8:])
        sorted_values = sorted_values[:9]
        sorted_labels = sorted_labels[:9]
        sorted_values.append(remaining)
        sorted_labels.append("* The Rest")

    return sorted_values, sorted_labels


def _shuffled_colors(today_tz, widget_id: int) -> list:
    colors = list(GRAPH_COLORS)
    random.seed(today_tz.month * widget_id)
    random.shuffle(colors)
    return colors


def get_graph_new_data(widget_id: int) -> List[PieGraphItem]:
    """
    Service function backing the /graph-by-tags/new endpoint.

    Returns a list of PieGraphItem objects for the given widget.
    """
    options = get_object_or_404(Option, id=1)
    widget_opts = _resolve_widget_options(options, widget_id)

    exclude_list = json.loads(widget_opts["exclude"])
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    target_date = today_tz - relativedelta(months=widget_opts["month"])
    target_month = target_date.month
    target_year = target_date.year

    colors = _shuffled_colors(today_tz, widget_id)

    tags, result = _get_tags_and_result(
        widget_opts["type_id"],
        widget_opts["tag_id"],
        exclude_list,
        target_month,
        target_year,
    )

    labels, values = _accumulate_labels_and_values(
        tags, widget_opts["type_id"], target_month, target_year
    )
    _append_untagged(result, values, labels)
    sorted_values, sorted_labels = _sort_and_cap(values, labels)

    graph_items = []
    for x, value in enumerate(sorted_values):
        graph_items.append(
            PieGraphItem(
                key=x,
                title=sorted_labels[x],
                value=abs(value),
                color=colors[x],
            )
        )

    service_logger.debug(f"Graph (new) data retrieved : {widget_id}")
    return graph_items


def get_graph_data(widget_id: int) -> GraphOut:
    """
    Service function backing the /graph-by-tags/get endpoint.

    Returns a GraphOut object for the given widget.
    """
    options = get_object_or_404(Option, id=1)
    widget_opts = _resolve_widget_options(options, widget_id)

    exclude_list = json.loads(widget_opts["exclude"])
    today = timezone.now()
    tz_timezone = pytz.timezone(os.environ.get("TIMEZONE"))
    today_tz = today.astimezone(tz_timezone).date()
    target_date = today_tz - relativedelta(months=widget_opts["month"])
    target_month = target_date.month
    target_year = target_date.year

    colors = _shuffled_colors(today_tz, widget_id)

    tags, result = _get_tags_and_result(
        widget_opts["type_id"],
        widget_opts["tag_id"],
        exclude_list,
        target_month,
        target_year,
    )

    labels, values = _accumulate_labels_and_values(
        tags, widget_opts["type_id"], target_month, target_year
    )
    _append_untagged(result, values, labels)

    if not values:
        values.append(0)
    if not labels:
        labels.append("None")

    dataset = GraphDataset(
        label=widget_opts["graph_name"],
        data=values,
        backgroundColor=colors,
        hoverOffset=4,
    )
    graph_object = GraphOut(labels=labels, datasets=[dataset])
    service_logger.debug(f"Graph data retrieved : {widget_id}")
    return graph_object
