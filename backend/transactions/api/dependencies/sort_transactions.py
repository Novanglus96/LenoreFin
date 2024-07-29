def sort_transactions(
    transactions: QuerySet[Transaction],
    asc: bool = True,
):
    """
    The function `sort_transactions` returns the provided transactions sorted.

    Args:
        transactions (QuerySet[Transaction]): A list of transactions to sort
        asc (bool): Perform a full (all objects) sort order update
    Returns:
        QuerySet[Transaction]: Sorted QuerySet of Transaction objects.
    """
    if asc:
        transactions = transactions.annotate(
            custom_order=Case(
                When(status_id=1, then=Value(2)),
                When(status_id=2, then=Value(0)),
                When(status_id=3, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by(
            "custom_order",
            "transaction_date",
            "-total_amount",
            "id",
        )
    else:
        transactions = transactions.annotate(
            custom_order=Case(
                When(status_id=1, then=Value(2)),
                When(status_id=2, then=Value(0)),
                When(status_id=3, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by(
            "-custom_order",
            "-transaction_date",
            "total_amount",
            "-id",
        )

    return transactions
