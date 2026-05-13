from accounts.dto import (
    DomainAccount,
    DomainAccountType,
    DomainBank,
    DomainFillObject,
    DomainTargetObject,
    DomainDatasetObject,
    DomainGraphData,
    DomainForecast,
)
from accounts.api.schemas.account import AccountOut
from accounts.api.schemas.bank import BankOut
from accounts.api.schemas.account_type import AccountTypeOut
from accounts.api.schemas.forecast import (
    TargetObject,
    FillObject,
    DatasetObject,
    GraphData,
    ForecastOut,
)


def domain_bank_to_schema(
    bank: DomainBank,
) -> BankOut:
    if bank is not None:
        return BankOut(id=bank.id, bank_name=bank.bank_name)
    else:
        return None


def domain_account_type_to_schema(
    account_type: DomainAccountType,
) -> AccountTypeOut:
    if account_type is not None:
        return AccountTypeOut(
            id=account_type.id,
            account_type=account_type.account_type,
            color=account_type.color,
            icon=account_type.icon,
            slug=account_type.slug,
            is_system=account_type.is_system,
        )
    else:
        return None


def domain_account_to_schema(
    account: DomainAccount,
) -> AccountOut:
    if account is not None:
        return AccountOut(
            id=account.id,
            account_name=account.account_name,
            account_type=domain_account_type_to_schema(account.account_type),
            opening_balance=account.opening_balance,
            annual_rate=account.annual_rate,
            due_date=account.due_date,
            active=account.active,
            open_date=account.open_date,
            statement_date=account.statement_date,
            statement_cycle_length=account.statement_cycle_length,
            statement_cycle_period=account.statement_cycle_period,
            credit_limit=account.credit_limit,
            rewards_amount=account.rewards_amount,
            available_credit=account.available_credit,
            balance=account.balance,
            bank=domain_bank_to_schema(account.bank),
            statement_balance=account.statement_balance,
            funding_account=domain_account_to_schema(account.funding_account),
            calculate_payments=account.calculate_payments,
            calculate_interest=account.calculate_interest,
            payment_strategy=account.payment_strategy,
            payment_amount=account.payment_amount,
            minimum_payment_amount=account.minimum_payment_amount,
            statement_day=account.statement_day,
            due_day=account.due_day,
            pay_day=account.pay_day,
            interest_deposit_day=account.interest_deposit_day,
            is_parent_account=account.is_parent_account,
            parent_account_id=account.parent_account_id,
            interest_child_account_id=account.interest_child_account_id,
            current_yr_rewards=account.current_yr_rewards,
            last_yr_rewards=account.last_yr_rewards,
        )
    else:
        return None


def domain_target_object_to_schema(
    target: DomainTargetObject,
) -> TargetObject:
    return TargetObject(value=target.value)


def domain_fill_object_to_schema(fill: DomainFillObject) -> FillObject:
    if fill is not None:
        return FillObject(
            target=domain_target_object_to_schema(fill.target),
            above=fill.above,
            below=fill.below,
        )
    else:
        return None


def domain_dataset_object_to_schema(
    dataset: DomainDatasetObject,
) -> DatasetObject:
    return DatasetObject(
        borderColor=dataset.borderColor,
        backgroundColor=dataset.backgroundColor,
        tension=dataset.tension,
        data=dataset.data,
        fill=domain_fill_object_to_schema(dataset.fill),
        pointStyle=dataset.pointStyle,
        radius=dataset.radius,
        hitRadius=dataset.hitRadius,
        hoverRadius=dataset.hoverRadius,
        label=dataset.label,
        hoverBackgroundColor=dataset.hoverBackgroundColor,
        hoverBorderColor=dataset.hoverBorderColor,
    )


def domain_graph_data_to_schema(graph: DomainGraphData) -> GraphData:
    return GraphData(
        labels=graph.labels,
        datasets=[domain_dataset_object_to_schema(ds) for ds in graph.datasets],
    )


def domain_forecast_to_schema(forecast: DomainForecast) -> ForecastOut:
    return ForecastOut(
        labels=forecast.labels,
        datasets=[
            domain_dataset_object_to_schema(ds) for ds in forecast.datasets
        ],
    )
