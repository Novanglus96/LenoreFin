from ninja import Schema
from typing import List, Optional
from datetime import date
from pydantic import ConfigDict, condecimal

AmountDecimal = condecimal(max_digits=12, decimal_places=2)


# The class BucketIn is a schema for validating Buckets.
class BucketIn(Schema):
    name: str
    # What this bucket is fed each paycheck. The contribution is the money; the
    # bucket is the standing plan for it.
    contribution_per_paycheck: AmountDecimal
    active: bool
    account_id: Optional[int] = None
    reminder_id: Optional[int] = None
    # Null means "work it out from the budgets and obligations"; a number is a
    # floor the contribution to this bucket may not go below in any mode.
    minimum_per_paycheck: Optional[AmountDecimal] = None
    target_balance: Optional[AmountDecimal] = None
    target_date: Optional[date] = None
    sweep: bool = False
    # Relative weight when several buckets sweep the remainder.
    sweep_share: int = 1
    priority: int = 100
    # Whether the planner may borrow from this account to bridge a gap.
    lendable: bool = True
    # Whether the card rewards are cashed into this account.
    receives_rewards: bool = False
    budget_ids: List[int] = []
    # The spending this bucket claims. A claim, not a source of funding: it is
    # how the review finds the budgets that ought to exist and do not.
    scope_tag_ids: List[int] = []


# The class BucketOut is a schema for representing Buckets.
class BucketOut(Schema):
    id: int
    name: str
    contribution_per_paycheck: AmountDecimal
    active: bool
    account_id: Optional[int] = None
    reminder_id: Optional[int] = None
    minimum_per_paycheck: Optional[AmountDecimal] = None
    target_balance: Optional[AmountDecimal] = None
    target_date: Optional[date] = None
    sweep: bool
    sweep_share: int
    priority: int
    lendable: bool
    receives_rewards: bool
    budget_ids: List[int] = []
    budget_names: List[str] = []
    scope_tag_ids: List[int] = []
    # Convenience for the table, so it need not join accounts client-side.
    account_name: Optional[str] = None
    # What the linked reminder actually moves, against which
    # contribution_per_paycheck is compared to detect drift. None when no
    # reminder is linked.
    reminder_amount: Optional[AmountDecimal] = None

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def resolve_account_name(obj):
        return obj.account.account_name if obj.account_id else None

    @staticmethod
    def resolve_reminder_amount(obj):
        return obj.reminder.amount if obj.reminder_id else None

    @staticmethod
    def resolve_budget_ids(obj):
        return [b.id for b in obj.budgets.all()]

    @staticmethod
    def resolve_scope_tag_ids(obj):
        return [t.id for t in obj.scope_tags.all()]

    @staticmethod
    def resolve_budget_names(obj):
        return [b.name for b in obj.budgets.all()]


# The class BucketsWithTotals is a schema for representing Buckets with totals.
class BucketsWithTotals(Schema):
    buckets: List[BucketOut]
    per_paycheck_total: AmountDecimal
    emergency_paycheck_total: AmountDecimal
    total_emergency: AmountDecimal

    model_config = ConfigDict(from_attributes=True)
