"""Production is at 0010 with Contributions; 0011 must carry them over intact."""

from decimal import Decimal as D

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

BEFORE = [("planning", "0010_detectedrecurring_suggested_fields")]
AFTER = [("planning", "0011_buckets_and_savings_plan")]


@pytest.mark.django_db(transaction=True)
def test_contributions_become_buckets_and_caps_become_goals():
    executor = MigrationExecutor(connection)
    executor.migrate(BEFORE)
    old = executor.loader.project_state(BEFORE).apps
    Contribution = old.get_model("planning", "Contribution")
    ContribRule = old.get_model("planning", "ContribRule")
    Contribution.objects.create(
        contribution="Vacation", per_paycheck="175.00", emergency_amt="150.00",
        emergency_diff="25.00", cap="4000.00", active=True,
    )
    Contribution.objects.create(
        contribution="Charity", per_paycheck="15.00", emergency_amt="15.00",
        emergency_diff="0.00", cap="0.00", active=False,
    )
    ContribRule.objects.create(rule="Remainder to Vacation", cap="No Cap", order=3)

    executor = MigrationExecutor(connection)
    executor.loader.build_graph()
    executor.migrate(AFTER)
    new = executor.loader.project_state(AFTER).apps
    Bucket = new.get_model("planning", "Bucket")
    WindfallRule = new.get_model("planning", "WindfallRule")

    vacation = Bucket.objects.get(name="Vacation")
    assert vacation.contribution_per_paycheck == D("175.00")
    assert vacation.goal_amount == D("4000.00")
    assert vacation.active is True
    charity = Bucket.objects.get(name="Charity")
    assert charity.goal_amount is None
    assert charity.active is False
    rule = WindfallRule.objects.get()
    assert (rule.rule, rule.cap, rule.order, rule.bucket_id) == ("Remainder to Vacation", "No Cap", 3, None)
