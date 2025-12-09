from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import Budget
from planning.api.schemas.budget import (
    BudgetIn,
    BudgetOut,
    BudgetWithTotal,
    BudgetQuery,
)
from reminders.models import Repeat
from django.shortcuts import get_object_or_404
from typing import List
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from administration.api.dependencies.get_todays_date_timezone_adjusted import (
    get_todays_date_timezone_adjusted,
)
from transactions.api.dependencies.get_transactions_by_tag import (
    get_transactions_by_tag,
)
import logging

api_logger = logging.getLogger("api")
db_logger = logging.getLogger("db")
error_logger = logging.getLogger("error")
task_logger = logging.getLogger("task")

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
        api_logger.info(f"Budget created : {payload.name}")
        return {"id": budget.id}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Budget not created : budget exists ({payload.name})"
            )
            error_logger(f"Budget not created : budget exists ({payload.name})")
            raise HttpError(400, "Budget already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Budget not created : db integrity error")
            error_logger.error("Budget not created : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Budget not created")
        error_logger.error(f"{str(e)}")
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
        api_logger.info(f"Budget updated : {budget.name}")
        return {"success": True}
    except IntegrityError as integrity_error:
        # Check if the integrity error is due to a duplicate
        if "unique constraint" in str(integrity_error).lower():
            api_logger.error(
                f"Budget not updated : budget exists ({payload.budget})"
            )
            error_logger.error(
                f"Budget not updated : budget exists ({payload.budget})"
            )
            raise HttpError(400, "Budget already exists")
        else:
            # Log other types of integry errors
            api_logger.error("Budget not updated : db integrity error")
            error_logger.error("Budget not updated : db integrity error")
            raise HttpError(400, "DB integrity error")
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Budget not updated")
        error_logger.error(f"{str(e)}")
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
        api_logger.debug(f"Budget retrieved : {budget.name}")
        return budget
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Budget not retrieved")
        error_logger.error(f"{str(e)}")
        raise HttpError(500, f"Record retrieval error: {str(e)}")


@budget_router.get("/list", response=List[BudgetWithTotal])
def list_budgets(
    request,
    query: BudgetQuery = Query(...),
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
        if query.widget:
            budgets = budgets.filter(widget=True)

        for budget in budgets:
            # Create the BudgetWithTotals object
            transactions = []
            # Get transactions and total for budget
            start_date, end_date = calculate_repeat_window(
                budget.start_day, budget.repeat
            )
            transactions = get_transactions_by_tag(
                end_date, False, start_date, json.loads(budget.tag_ids), False
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
                used_percentage = min(
                    100, round(abs(total) / abs(budget_total) * 100)
                )
            else:
                used_percentage = 0
            new_budget_with_total = BudgetWithTotal(
                budget=budget,
                transactions=unique_transactions,
                used_total=total,
                used_percentage=used_percentage,
                remaining_percentage=100 - used_percentage,
            )
            budgets_with_totals.append(new_budget_with_total)
        api_logger.debug("Budget list retrieved")
        return budgets_with_totals
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Budget list not retrieved")
        error_logger.error(f"{str(e)}")
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
        api_logger.info(f"Budget deleted : {budget_name}")
        return {"success": True}
    except Exception as e:
        # Log other types of exceptions
        api_logger.error("Budget not deleted")
        error_logger.error(f"{str(e)}")
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
