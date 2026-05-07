from planning.dto import (
    DomainBudget,
    DomainCalculationRule,
    DomainCalculator,
    DomainContribRule,
    DomainContribution,
    DomainContributionWithTotals,
    DomainNote,
    DomainPlanningGraph,
    DomainPlanningGraphList,
    DomainDataSetObject,
    DomainFillObject,
    DomainForecast,
    DomainGraphData,
    DomainTargetObject,
)
from planning.api.schemas.budget import BudgetOut
from planning.api.schemas.calculator import CalculationRuleOut, CalculatorOut
from planning.api.schemas.contrib_rule import ContribRuleOut
from planning.api.schemas.contribution import (
    ContributionOut,
    ContributionWithTotals,
)
from planning.api.schemas.note import NoteOut
from planning.api.schemas.planning_graph import (
    PlanningGraphList,
    PlanningGraphOut,
)
from planning.api.schemas.retirement import (
    TargetObject,
    FillObject,
    DatasetObject,
    GraphData,
    ForecastOut,
)
from reminders.mappers import domain_repeat_to_schema
from accounts.mappers import domain_graph_data_to_schema
from transactions.mappers import domain_transaction_to_schema


def domain_budget_to_schema(
    budget: DomainBudget,
) -> BudgetOut:
    return BudgetOut(
        id=budget.id,
        tag_ids=budget.tag_ids,
        name=budget.name,
        amount=budget.amount,
        roll_over=budget.roll_over,
        repeat=domain_repeat_to_schema(budget.repeat),
        start_day=budget.start_day,
        roll_over_amt=budget.roll_over_amt,
        active=budget.active,
        widget=budget.widget,
        next_start=budget.next_start,
    )


def domain_calculation_rule_to_schema(
    rule: DomainCalculationRule,
) -> CalculationRuleOut:
    return CalculationRuleOut(
        id=rule.id,
        tag_ids=rule.tag_ids,
        name=rule.name,
        source_account_id=rule.source_account_id,
        destination_account_id=rule.destination_account_id,
    )


def domain_calculator_to_schema(calc: DomainCalculator) -> CalculatorOut:
    return CalculatorOut(
        rule=calc.rule,
        transfers=[
            domain_transaction_to_schema(tran) for tran in calc.transfers
        ],
        transactions=[
            domain_transaction_to_schema(tran) for tran in calc.transactions
        ],
    )


def domain_contrib_rule_to_schema(rule: DomainContribRule) -> ContribRuleOut:
    return ContribRuleOut(
        id=rule.id, rule=rule.rule, cap=rule.cap, order=rule.order
    )


def domain_contribution_to_schema(
    contrib: DomainContribution,
) -> ContributionOut:
    return ContributionOut(
        id=contrib.id,
        contribution=contrib.contribution,
        per_paycheck=contrib.per_paycheck,
        emergency_diff=contrib.emergency_diff,
        emergency_amt=contrib.emergency_amt,
        cap=contrib.cap,
        active=contrib.active,
    )


def domain_contribution_with_totals_to_schema(
    contrib: DomainContributionWithTotals,
) -> ContributionWithTotals:
    return ContributionWithTotals(
        contributions=[
            domain_contribution_to_schema(dc) for dc in contrib.contributions
        ],
        per_paycheck_total=contrib.per_paycheck_total,
        emergency_paycheck_total=contrib.emergency_paycheck_total,
        total_emergency=contrib.total_emergency,
    )


def domain_note_to_schema(note: DomainNote) -> NoteOut:
    return NoteOut(
        id=note.id, note_text=note.note_text, note_date=note.note_date
    )


def domain_planning_graph_to_schema(
    graph: DomainPlanningGraph,
) -> PlanningGraphOut:
    return PlanningGraphOut(
        data=domain_graph_data_to_schema(graph.data),
        year1=graph.year1,
        year2=graph.year2,
        year1_avg=graph.year1_avg,
        year2_avg=graph.year2_avg,
        pretty_name=graph.pretty_name,
        key_name=graph.key_name,
    )


def domain_planning_graph_list_to_schema(
    graph: DomainPlanningGraphList,
) -> PlanningGraphList:
    return PlanningGraphList(
        title=graph.title,
        data=[domain_planning_graph_to_schema(gr) for gr in graph.data],
    )


def domain_target_object_to_schema(obj: DomainTargetObject) -> TargetObject:
    return TargetObject(value=obj.value)


def domain_fill_object_to_schema(obj: DomainFillObject) -> FillObject:
    return FillObject(
        target=domain_target_object_to_schema(obj.target),
        above=obj.above,
        below=obj.below,
    )


def domain_dataset_object_to_schema(data: DomainDataSetObject) -> DatasetObject:
    return DatasetObject(
        borderColor=data.borderColor,
        backgroundColor=data.backgroundColor,
        tension=data.tension,
        data=data.data,
        pointStyle=data.pointStyle,
        radius=data.radius,
        hitRadius=data.hitRadius,
        hoverRadius=data.hoverRadius,
        label=data.label,
        hoverBackgroundColor=data.hoverBackgroundColor,
        hoverBorderColor=data.hoverBorderColor,
    )


def domain_retirement_graph_data_to_schema(graph: DomainGraphData) -> GraphData:
    return GraphData(
        labels=graph.labels,
        datasets=[
            domain_dataset_object_to_schema(obj) for obj in graph.datasets
        ],
    )


def domain_forecast(forecast: DomainForecast) -> ForecastOut:
    return ForecastOut(
        labels=forecast.labels,
        datasets=[
            domain_dataset_object_to_schema(obj) for obj in forecast.datasets
        ],
    )
