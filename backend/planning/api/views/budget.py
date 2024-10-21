from ninja import Router, Query
from django.db import IntegrityError
from ninja.errors import HttpError
from planning.models import Budget
from planning.api.schemas.budget import BudgetIn, BudgetOut, BudgetWithTotal
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
        budget.roll_over_amt = payload.roll_over_amt
        budget.active = payload.active
        budget.widget = payload.widget
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
def list_budgets(request):
    """
    The function `list_budgets` retrieves a list of budgets,
    ordered by id ascending.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        BudgetOut: a list of budget objects
    """

    try:
        qs = Budget.objects.all().order_by("-active", "id")
        active_contribs = qs.filter(active=True)

        # Compute totals (this can be customized based on your business logic)
        per_paycheck_total = sum(
            [contrib.per_paycheck for contrib in active_contribs]
        )
        emergency_paycheck_total = sum(
            [contrib.emergency_amt for contrib in active_contribs]
        )
        total_emergency = sum(
            [contrib.emergency_diff for contrib in active_contribs]
        )

        # Create the BudgetWithTotals object
        budgets_with_totals = BudgetWithTotals(
            budgets=list(qs),
            per_paycheck_total=per_paycheck_total,
            emergency_paycheck_total=emergency_paycheck_total,
            total_emergency=total_emergency,
        )
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
