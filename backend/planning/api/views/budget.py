from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import Budget
from planning.api.schemas.budget import BudgetIn, BudgetOut, BudgetWithTotal
from reminders.models import Repeat
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
from transactions.api.dependencies.get_complete_transaction_list_with_totals import (
    get_complete_transaction_list_with_totals,
)
import json
from datetime import date, timedelta, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)

budget_router = Router(tags=["Budgets"])


@budget_router.post("/create")
def create_budget(request, payload: BudgetIn):
    """
    The function `create_budget` creates a budget

    Args:
        request ():
        payload (BudgetIn): An object using schema of BudgetIn.

    Returns:
        id: returns the id of the created budget
    """

    try:
        budget = Budget.objects.create(**payload.dict())
        logToDB(
            f"Budget created : {payload.name}",
            None,
            None,
            None,
            3001001,
            1,
        )
        return {"id": budget.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Budget not created : budget exists ({payload.name})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Budget already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Budget not created : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Budget not created : {str(e)}",
            None,
            None,
            None,
            3001901,
            2,
        )
        raise HttpError(500, "Record creation error")


@budget_router.put("/update/{budget_id}")
def update_budget(request, budget_id: int, payload: BudgetIn):
    """
    The function `update_budget` updates the budget specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        budget_id (int): the id of the budget to update
        payload (BudgetIn): a budget object

    Returns:
        success: True

    Raises:
        Http404: If the budget with the specified ID does not exist.
    """

    try:
        budget = get_object_or_404(Budget, id=budget_id)
        budget.tag_ids = payload.tag_ids
        budget.name = payload.name
        budget.amount = payload.amount
        budget.roll_over = payload.roll_over
        budget.repeat_id = payload.repeat_id
        budget.start_day = payload.start_day
        if payload.roll_over_amt:
            budget.roll_over_amt = payload.roll_over_amt
        budget.active = payload.active
        budget.widget = payload.widget
        budget.next_start = payload.next_start
        budget.save()
        logToDB(
            f"Budget updated : {budget.name}",
            None,
            None,
            None,
            3001002,
            1,
        )
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            logToDB(
                f"Budget not updated : budget exists ({payload.budget})",
                None,
                None,
                None,
                3001004,
                2,
            )
            raise HttpError(400, "Budget already exists")
        else:
            # Log other types of integry errors
            logToDB(
                "Budget not updated : db integrity error",
                None,
                None,
                None,
                3001005,
                2,
            )
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Budget not updated : {str(e)}",
            None,
            None,
            None,
            3001902,
            2,
        )
        raise HttpError(500, "Record update error")


@budget_router.get("/get/{budget_id}", response=BudgetOut)
def get_budget(request, budget_id: int):
    """
    The function `get_budget` retrieves the budget by id

    Args:
        request (HttpRequest): The HTTP request object.
        budget_id (int): The id of the budget to retrieve.

    Returns:
        BudgetOut: the budget object

    Raises:
        Http404: If the budget with the specified ID does not exist.
    """

    try:
        budget = get_object_or_404(Budget, id=budget_id)
        logToDB(
            f"Budget retrieved : {budget.name}",
            None,
            None,
            None,
            3001006,
            1,
        )
        return budget
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Budget not retrieved : {str(e)}",
            None,
            None,
            None,
            3001904,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@budget_router.get("/list", response=List[BudgetWithTotal])
def list_budgets(
    request,
    widget: Optional[bool] = Query(True),
):
    """
    The function `list_budgets` retrieves a list of budgets,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        BudgetOut: a list of budget objects
    """

    try:
        budgets_with_totals = []
        budgets = (
            Budget.objects.all().filter(active=True).order_by("name", "id")
        )
        if widget:
            budgets = budgets.filter(widget=True)

        for budget in budgets:
            # Create the BudgetWithTotals object
            transactions = []
            # Get transactions and total for budget
            start_date, end_date = calculate_repeat_window(
                budget.start_day, budget.repeat
            )
            transactions, balances = get_complete_transaction_list_with_totals(
                end_date,
                1,
                False,
                False,
                start_date,
                False,
                [],
                json.loads(budget.tag_ids),
                True,
            )
            total = 0
            unique_transactions = []
            for transaction in transactions:
                if transaction not in unique_transactions:
                    unique_transactions.append(transaction)
            for transaction in unique_transactions:
                total += transaction.tag_total
            budget_total = budget.amount
            if budget.roll_over:
                budget_total += budget.roll_over_amt
            if total:
                used_percentage = round(abs(total) / (abs(budget_total)) * 100)
            else:
                used_percentage = 0
            new_budget_with_total = BudgetWithTotal(
                budget=budget,
                transactions=unique_transactions,
                used_total=total,
                used_percentage=used_percentage,
            )
            budgets_with_totals.append(new_budget_with_total)
        logToDB(
            "Budget list retrieved",
            None,
            None,
            None,
            3001007,
            1,
        )
        return budgets_with_totals
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Budget list not retrieved : {str(e)}",
            None,
            None,
            None,
            3001907,
            2,
        )
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@budget_router.delete("/delete/{budget_id}")
def delete_budget(request, budget_id: int):
    """
    The function `delete_budget` deletes the budget specified by id.

    Args:
        request (HttpRequest): The HTTP request object.
        budget_id (int): the id of the budget to delete

    Returns:
        success: True

    Raises:
        Http404: If the budget with the specified ID does not exist.
    """

    try:
        budget = get_object_or_404(Budget, id=budget_id)
        budget_name = budget.name
        budget.delete()
        logToDB(
            f"Budget deleted : {budget_name}",
            None,
            None,
            None,
            3001003,
            1,
        )
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        logToDB(
            f"Budget not deleted : {str(e)}",
            None,
            None,
            None,
            3001903,
            2,
        )
        raise HttpError(500, "Record retrieval error")


def calculate_repeat_window(start_date: datetime, repeat: Repeat) -> tuple:
    """
    Calculate the current repeat window (start and end date) based on the Repeat object.

    Args:
        start_date (datetime or date): The date when the repetition started.
        repeat (Repeat): The Repeat object containing the interval (days, weeks, months, years).

    Returns:
        tuple: A tuple of (window_start, window_end) for the current repeat window.
    """
    # Combine repeat fields into a single period using relativedelta
    total_period = relativedelta(
        days=repeat.days,
        weeks=repeat.weeks,
        months=repeat.months,
        years=repeat.years,
    )

    # Get the current date (you can use your timezone-adjusted function here)
    today = get_todays_date_timezone_adjusted()

    # Calculate how many total periods have passed since the start date
    periods_passed = 0
    current_period_start = start_date

    while current_period_start + total_period <= today:
        current_period_start += total_period
        periods_passed += 1

    window_start = current_period_start
    window_end = window_start + total_period + relativedelta(days=-1)

    return window_start, window_end
