from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from dateutil.relativedelta import relativedelta
from django.db.models import Q, Sum

from tags.models import MainTag, SubTag, Tag
from transactions.models import TransactionDetail, TransactionStatus


def compute_date_range(date_range_type: str, date_from=None, date_to=None):
    today = date.today()
    year = today.year
    month = today.month

    if date_range_type == "THIS_YEAR":
        return date(year, 1, 1), date(year, 12, 31)
    if date_range_type == "LAST_YEAR":
        return date(year - 1, 1, 1), date(year - 1, 12, 31)
    if date_range_type == "THIS_QUARTER":
        q_start_month = ((month - 1) // 3) * 3 + 1
        q_start = date(year, q_start_month, 1)
        q_end = q_start + relativedelta(months=3) - timedelta(days=1)
        return q_start, q_end
    if date_range_type == "LAST_QUARTER":
        q_start_month = ((month - 1) // 3) * 3 + 1
        lq_start = date(year, q_start_month, 1) - relativedelta(months=3)
        lq_end = lq_start + relativedelta(months=3) - timedelta(days=1)
        return lq_start, lq_end
    if date_range_type == "TRAILING_12":
        end = today
        start = today - relativedelta(months=12) + timedelta(days=1)
        return start, end
    # CUSTOM
    return date_from, date_to


def _shift_back_one_year(start: date, end: date):
    return start - relativedelta(years=1), end - relativedelta(years=1)


def _get_status_ids(include_pending: bool):
    slugs = ["cleared", "reconciled", "archived"]
    if include_pending:
        slugs.append("pending")
    return list(
        TransactionStatus.objects.filter(slug__in=slugs).values_list("id", flat=True)
    )


def _resolve_tag_ids(tag_id=None, sub_tag_id=None, main_tag_id=None):
    if tag_id:
        return [tag_id]
    if sub_tag_id:
        return list(Tag.objects.filter(child_id=sub_tag_id).values_list("id", flat=True))
    if main_tag_id:
        return list(Tag.objects.filter(parent_id=main_tag_id).values_list("id", flat=True))
    return []


def _get_tag_label(tag_id=None, sub_tag_id=None, main_tag_id=None):
    if tag_id:
        try:
            t = Tag.objects.select_related("parent", "child").get(id=tag_id)
            return t.tag_name
        except Tag.DoesNotExist:
            return f"Tag {tag_id}"
    if sub_tag_id:
        try:
            return SubTag.objects.get(id=sub_tag_id).tag_name
        except SubTag.DoesNotExist:
            return f"SubTag {sub_tag_id}"
    if main_tag_id:
        try:
            return MainTag.objects.get(id=main_tag_id).tag_name
        except MainTag.DoesNotExist:
            return f"MainTag {main_tag_id}"
    return "Unknown"


def _build_base_qs(start: date, end: date, status_ids, account_ids):
    qs = TransactionDetail.objects.filter(
        transaction__transaction_date__gte=start,
        transaction__transaction_date__lte=end,
        transaction__status_id__in=status_ids,
    ).select_related("transaction", "transaction__source_account")

    if account_ids:
        qs = qs.filter(
            Q(transaction__source_account_id__in=account_ids)
            | Q(transaction__destination_account_id__in=account_ids)
        )
    return qs


def _sum_qs(qs) -> Decimal:
    result = qs.aggregate(total=Sum("detail_amt"))["total"]
    return result if result is not None else Decimal("0.00")


def _build_transaction_rows(qs):
    rows = []
    seen_tx = set()
    for detail in qs.select_related(
        "transaction", "transaction__source_account"
    ).order_by("transaction__transaction_date"):
        tx = detail.transaction
        if tx.id in seen_tx:
            continue
        seen_tx.add(tx.id)
        account_name = (
            tx.source_account.account_name if tx.source_account else ""
        )
        rows.append(
            {
                "id": tx.id,
                "date": tx.transaction_date,
                "description": tx.description,
                "amount": tx.total_amount,
                "account": account_name,
            }
        )
    return rows


def _month_label(year: int, month: int) -> str:
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ]
    return f"{month_names[month - 1]} {year}"


def _iter_months(start: date, end: date):
    current = date(start.year, start.month, 1)
    while current <= end:
        month_end = current + relativedelta(months=1) - timedelta(days=1)
        yield current, min(month_end, end)
        current = current + relativedelta(months=1)


def run_report(
    report_type: str,
    date_range_type: str,
    group_by: str,
    date_from: Optional[date],
    date_to: Optional[date],
    account_ids: list,
    tag_selections: list,
    show_transactions: bool,
    show_subtotal: bool,
    include_pending: bool,
):
    start, end = compute_date_range(date_range_type, date_from, date_to)
    status_ids = _get_status_ids(include_pending)

    if report_type == "TOTALS":
        return _run_totals(
            start, end, status_ids, account_ids, tag_selections,
            group_by, show_transactions, show_subtotal,
        )
    else:
        return _run_comparison(
            start, end, status_ids, account_ids, tag_selections,
            group_by, show_subtotal,
        )


def _run_totals(start, end, status_ids, account_ids, tag_selections, group_by, show_transactions, show_subtotal):
    base_qs = _build_base_qs(start, end, status_ids, account_ids)
    rows = []

    if group_by == "MONTH":
        all_tag_ids = _all_tag_ids_from_selections(tag_selections)
        if all_tag_ids is not None:
            month_qs = base_qs.filter(tag_id__in=all_tag_ids)
        else:
            month_qs = base_qs

        for month_start, month_end in _iter_months(start, end):
            m_qs = month_qs.filter(
                transaction__transaction_date__gte=month_start,
                transaction__transaction_date__lte=month_end,
            )
            total = _sum_qs(m_qs)
            row = {
                "label": _month_label(month_start.year, month_start.month),
                "total": total,
            }
            if show_transactions:
                row["transactions"] = _build_transaction_rows(m_qs)
            rows.append(row)
    else:
        # group_by == TAG
        if tag_selections:
            for sel in tag_selections:
                tag_ids = _resolve_tag_ids(
                    tag_id=sel.get("tag_id"),
                    sub_tag_id=sel.get("sub_tag_id"),
                    main_tag_id=sel.get("main_tag_id"),
                )
                label = _get_tag_label(
                    tag_id=sel.get("tag_id"),
                    sub_tag_id=sel.get("sub_tag_id"),
                    main_tag_id=sel.get("main_tag_id"),
                )
                filtered = base_qs.filter(tag_id__in=tag_ids) if tag_ids else base_qs.none()
                total = _sum_qs(filtered)
                row = {"label": label, "total": total}
                if show_transactions:
                    row["transactions"] = _build_transaction_rows(filtered)
                rows.append(row)
        else:
            total = _sum_qs(base_qs)
            row = {"label": "All Tags", "total": total}
            if show_transactions:
                row["transactions"] = _build_transaction_rows(base_qs)
            rows.append(row)

    result = {
        "report_type": "TOTALS",
        "group_by": group_by,
        "date_from": start,
        "date_to": end,
        "rows": rows,
    }
    if show_subtotal:
        result["subtotal"] = sum(r["total"] for r in rows)
    return result


def _run_comparison(start, end, status_ids, account_ids, tag_selections, group_by, show_subtotal):
    prior_start, prior_end = _shift_back_one_year(start, end)
    base1 = _build_base_qs(start, end, status_ids, account_ids)
    base2 = _build_base_qs(prior_start, prior_end, status_ids, account_ids)
    rows = []

    if group_by == "MONTH":
        # Overall totals only for COMPARISON + MONTH
        all_tag_ids = _all_tag_ids_from_selections(tag_selections)
        if all_tag_ids is not None:
            t1 = _sum_qs(base1.filter(tag_id__in=all_tag_ids))
            t2 = _sum_qs(base2.filter(tag_id__in=all_tag_ids))
        else:
            t1 = _sum_qs(base1)
            t2 = _sum_qs(base2)
        rows.append({
            "label": "Total",
            "period1_total": t1,
            "period2_total": t2,
            "difference": t1 - t2,
        })
    else:
        # group_by == TAG
        if tag_selections:
            for sel in tag_selections:
                tag_ids = _resolve_tag_ids(
                    tag_id=sel.get("tag_id"),
                    sub_tag_id=sel.get("sub_tag_id"),
                    main_tag_id=sel.get("main_tag_id"),
                )
                label = _get_tag_label(
                    tag_id=sel.get("tag_id"),
                    sub_tag_id=sel.get("sub_tag_id"),
                    main_tag_id=sel.get("main_tag_id"),
                )
                t1 = _sum_qs(base1.filter(tag_id__in=tag_ids)) if tag_ids else Decimal("0.00")
                t2 = _sum_qs(base2.filter(tag_id__in=tag_ids)) if tag_ids else Decimal("0.00")
                rows.append({
                    "label": label,
                    "period1_total": t1,
                    "period2_total": t2,
                    "difference": t1 - t2,
                })
        else:
            t1 = _sum_qs(base1)
            t2 = _sum_qs(base2)
            rows.append({
                "label": "All Tags",
                "period1_total": t1,
                "period2_total": t2,
                "difference": t1 - t2,
            })

    result = {
        "report_type": "COMPARISON",
        "group_by": group_by,
        "date_from": start,
        "date_to": end,
        "period2_from": prior_start,
        "period2_to": prior_end,
        "rows": rows,
    }
    if show_subtotal:
        result["subtotal"] = sum(r.get("period1_total", Decimal("0")) for r in rows)
        result["subtotal2"] = sum(r.get("period2_total", Decimal("0")) for r in rows)
    return result


def _all_tag_ids_from_selections(tag_selections):
    """Return flat list of all resolved Tag IDs, or None if selections is empty (= all tags)."""
    if not tag_selections:
        return None
    ids = []
    for sel in tag_selections:
        ids.extend(_resolve_tag_ids(
            tag_id=sel.get("tag_id"),
            sub_tag_id=sel.get("sub_tag_id"),
            main_tag_id=sel.get("main_tag_id"),
        ))
    return ids
