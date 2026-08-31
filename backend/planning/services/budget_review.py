"""Comparing what the budgets say against what actually happened.

Budgets are the only thing the savings plan acts on. That is deliberate: a
budget is a decision, and measured spending is only evidence about one. But a
decision nobody revisits drifts, and a category nobody wrote down at all is
invisible — this household's gift spending ran at 4,072 a year against a 1,995
budget for exactly that reason, because Christmas was written down and birthdays
were not.

So this is the other half of the loop. It reads twelve months of tagged spending
and says where the budgets disagree with it: raise this one, lower that one,
write one for the spending that has none. Accepting a suggestion changes a
budget, and changing a budget changes the plan. Nothing here alters anything on
its own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum

from planning.models import Budget, Contribution
from planning.services.budget_math import (
    amount_per_year,
    budget_tag_ids,
    spending_budgets,
)
from tags.models import Tag
from transactions.models import TransactionDetail

# Below these, a difference is noise rather than a decision to revisit. Both
# have to be cleared: 10% of a 60-a-year budget is six pounds, and nobody wants
# to be told about six pounds.
MATERIAL_FRACTION = Decimal("0.10")
MATERIAL_AMOUNT = Decimal("50")
# Unbudgeted spending has no percentage to compare against, so it only needs to
# clear an absolute bar — but a higher one, because writing a budget is a chore.
MATERIAL_NEW_BUDGET = Decimal("100")


@dataclass
class BudgetSuggestion:
    kind: str  # raise | lower | create
    budget_id: int | None
    budget_name: str
    tag_names: list[str]
    budgeted_per_year: Decimal
    measured_per_year: Decimal
    suggested_per_year: Decimal
    # The same figure in the budget's own cadence, which is what the user would
    # actually type into the budget form.
    suggested_amount: Decimal
    cadence: str
    per_paycheck_effect: Decimal
    contribution: str | None
    why: str


@dataclass
class BudgetReview:
    generated_for: date
    window_days: int
    suggestions: list[BudgetSuggestion] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _per_year(amount: Decimal, repeat) -> tuple[Decimal, str]:
    """A budget's yearly cost, and the cadence it is stated in."""
    if repeat is None or not amount:
        return Decimal("0.00"), "one-off"
    per_year = amount_per_year(amount, repeat)
    if per_year <= 0:
        return Decimal("0.00"), "one-off"
    return per_year, str(repeat)


def _measured_by_tag(today: date, window_days: int) -> dict[int, Decimal]:
    """Twelve months of spending, per tag.

    One aggregate query rather than a walk over transactions: this runs
    alongside a plan that already costs a couple of seconds, and the whole point
    of it is to be cheap enough to show every time.
    """
    since = today - timedelta(days=window_days)
    rows = (
        TransactionDetail.objects.filter(
            transaction__transaction_date__gte=since,
            transaction__transaction_date__lt=today,
        )
        .exclude(transaction__status__slug="archived")
        .values("tag_id")
        .annotate(total=Sum("detail_amt"))
    )
    measured: dict[int, Decimal] = {}
    for row in rows:
        if row["tag_id"] is None or row["total"] is None:
            continue
        # Spending is stored negative; a refund nets off against it.
        spent = -row["total"]
        if spent > 0:
            measured[row["tag_id"]] = spent
    return measured


def _tag_label(tag: Tag) -> str:
    parent = tag.parent.tag_name if tag.parent else "?"
    return f"{parent}/{tag.child.tag_name}" if tag.child else parent


def review_budgets(today: date, window_days: int = 365) -> BudgetReview:
    """Where the budgets and the last twelve months disagree."""
    measured = _measured_by_tag(today, window_days)
    review = BudgetReview(generated_for=today, window_days=window_days)

    per_paycheck = Decimal("26.0893")
    budget_owner: dict[int, str] = {}
    for contribution in Contribution.objects.filter(
        active=True
    ).prefetch_related("budgets"):
        for budget in contribution.budgets.all():
            budget_owner[budget.pk] = contribution.contribution

    # Only the budgets that speak: leaves and parents, never a child. A
    # child's spending is inside its parent's total, so comparing both against
    # the same tags is the double count this hierarchy exists to end.
    budgets = spending_budgets(
        Budget.objects.filter(active=True)
        .select_related("repeat", "parent")
        .prefetch_related("children__repeat")
    )
    tags_of: dict[int, list[int]] = {
        budget.pk: budget_tag_ids(budget) for budget in budgets
    }

    # Two budgets covering the same tag both look overspent against the same
    # money. This household budgets Christmas twice over — a 1,995 parent and
    # twenty per-person budgets covering the same tags — so comparing either
    # against what was spent says nothing, and "raise John's gift budget from
    # 100 to 524" would be advice founded on money the parent budget already
    # accounts for.
    owners: dict[int, list[int]] = {}
    for budget_pk, tag_ids in tags_of.items():
        for tag_id in tag_ids:
            owners.setdefault(tag_id, []).append(budget_pk)
    ambiguous = {
        budget_pk
        for budget_pk, tag_ids in tags_of.items()
        if any(len(owners[tag_id]) > 1 for tag_id in tag_ids)
    }
    review.suggestions.extend(
        _overlaps(budgets, tags_of, owners, ambiguous, per_paycheck)
    )

    covered: set[int] = set()
    for budget in budgets:
        tag_ids = tags_of[budget.pk]
        covered.update(tag_ids)
        if budget.pk in ambiguous:
            continue

        spent = sum(
            (measured.get(tid, Decimal("0")) for tid in tag_ids), Decimal("0")
        )
        budgeted, cadence = _per_year(budget.planned_amount, budget.repeat)
        if budgeted <= 0 and spent <= 0:
            continue

        gap = spent - budgeted
        if abs(gap) < MATERIAL_AMOUNT:
            continue
        if budgeted > 0 and abs(gap) / budgeted < MATERIAL_FRACTION:
            continue

        planned = budget.planned_amount
        occurrences = (budgeted / abs(planned)) if planned else None
        suggested_amount = (
            (spent / occurrences).quantize(Decimal("0.01"))
            if occurrences
            else spent
        )
        review.suggestions.append(
            BudgetSuggestion(
                kind="raise" if gap > 0 else "lower",
                budget_id=budget.pk,
                budget_name=budget.name,
                tag_names=[
                    _tag_label(t)
                    for t in Tag.objects.filter(pk__in=tag_ids).select_related(
                        "parent", "child"
                    )
                ],
                budgeted_per_year=budgeted,
                measured_per_year=spent.quantize(Decimal("0.01")),
                suggested_per_year=spent.quantize(Decimal("0.01")),
                suggested_amount=suggested_amount,
                cadence=cadence,
                per_paycheck_effect=(gap / per_paycheck).quantize(
                    Decimal("0.01")
                ),
                contribution=budget_owner.get(budget.pk),
                why=(
                    f"{budget.name} budgets {budgeted} a year and the last "
                    f"twelve months came to {spent.quantize(Decimal('0.01'))}. "
                    f"{'Raising' if gap > 0 else 'Lowering'} it to "
                    f"{suggested_amount} {cadence.lower()} moves the plan by "
                    f"about {abs(gap / per_paycheck).quantize(Decimal('0.01'))} "
                    f"a paycheck."
                ),
            )
        )

    review.suggestions.extend(_unbudgeted(measured, covered, per_paycheck))
    if ambiguous:
        review.notes.append(
            f"{len(ambiguous)} budgets cover tags another budget also covers, "
            "so they cannot be checked against what was spent. Pick one budget "
            "per tag — the parent or the children, not both."
        )
    review.suggestions.sort(
        key=lambda s: abs(s.per_paycheck_effect), reverse=True
    )
    return review


def _overlaps(
    budgets: list[Budget],
    tags_of: dict[int, list[int]],
    owners: dict[int, list[int]],
    ambiguous: set[int],
    per_paycheck: Decimal,
) -> list[BudgetSuggestion]:
    """Budgets that cover the same spending as each other, reported once each.

    Not a number to change but a decision to make, so it carries no suggested
    amount: whether Christmas is one budget of 1,995 or twenty budgets naming
    twenty people is a question about how the household wants to think, and
    either answer is fine as long as it is only one of them.
    """
    if not ambiguous:
        return []

    by_pk = {budget.pk: budget for budget in budgets}
    seen: set[int] = set()
    suggestions: list[BudgetSuggestion] = []

    for budget_pk in sorted(ambiguous):
        if budget_pk in seen:
            continue
        group: set[int] = set()
        for tag_id in tags_of[budget_pk]:
            group.update(owners[tag_id])
        group &= ambiguous
        seen.update(group)
        names = sorted(by_pk[pk].name for pk in group)
        suggestions.append(
            BudgetSuggestion(
                kind="overlap",
                budget_id=budget_pk,
                budget_name=names[0],
                tag_names=[],
                budgeted_per_year=Decimal("0.00"),
                measured_per_year=Decimal("0.00"),
                suggested_per_year=Decimal("0.00"),
                suggested_amount=Decimal("0.00"),
                cadence="",
                per_paycheck_effect=Decimal("0.00"),
                contribution=None,
                why=(
                    f"{len(names)} budgets cover the same tags: "
                    f"{', '.join(names[:6])}"
                    + (f" and {len(names) - 6} more" if len(names) > 6 else "")
                    + ". While they overlap, none of them can be compared "
                    "against what was actually spent. Keep the parent or the "
                    "children, not both."
                ),
            )
        )
    return suggestions


def _unbudgeted(
    measured: dict[int, Decimal], covered: set[int], per_paycheck: Decimal
) -> list[BudgetSuggestion]:
    """Spending a bucket owns that no budget describes.

    Scoped to tags someone has linked to a contribution, because unscoped this
    is meaningless — transfers, income and card payments dwarf every real
    category, and a report led by "Transfer: 230,990 unbudgeted" is one nobody
    reads twice.
    """
    suggestions: list[BudgetSuggestion] = []
    for contribution in Contribution.objects.filter(active=True).prefetch_related(
        "tags__parent", "tags__child"
    ):
        loose = [
            tag
            for tag in contribution.tags.all()
            if tag.pk not in covered
            and measured.get(tag.pk, Decimal("0")) > 0
        ]
        if not loose:
            continue
        spent = sum(
            (measured[tag.pk] for tag in loose), Decimal("0")
        ).quantize(Decimal("0.01"))
        if spent < MATERIAL_NEW_BUDGET:
            continue
        names = [_tag_label(tag) for tag in loose]
        suggestions.append(
            BudgetSuggestion(
                kind="create",
                budget_id=None,
                budget_name=f"{contribution.contribution} (unbudgeted)",
                tag_names=names,
                budgeted_per_year=Decimal("0.00"),
                measured_per_year=spent,
                suggested_per_year=spent,
                suggested_amount=spent,
                cadence="Every Year",
                per_paycheck_effect=(spent / per_paycheck).quantize(
                    Decimal("0.01")
                ),
                contribution=contribution.contribution,
                why=(
                    f"{spent} a year was spent on {', '.join(names)}, which "
                    f"{contribution.contribution} is meant to cover and no "
                    f"budget describes. Until a budget says so the plan does "
                    f"not fund it, so {contribution.contribution} is short by "
                    f"about {(spent / per_paycheck).quantize(Decimal('0.01'))} "
                    f"a paycheck."
                ),
            )
        )
    return suggestions
