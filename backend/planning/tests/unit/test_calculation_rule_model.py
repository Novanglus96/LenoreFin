import pytest
from planning.models import CalculationRule
from django.db import IntegrityError


@pytest.mark.django_db
def test_calculation_rule_creation():
    calculation_rule = CalculationRule.objects.create(
        tag_ids="tag ids",
        name="Contribution Rule Name",
        source_account_id=1,
        destination_account_id=1,
    )

    assert calculation_rule.id is not None
    assert calculation_rule.tag_ids == "tag ids"
    assert calculation_rule.name == "Contribution Rule Name"
    assert calculation_rule.source_account_id == 1
    assert calculation_rule.destination_account_id == 1


@pytest.mark.django_db
def test_name_uniqueness():
    CalculationRule.objects.create(
        tag_ids="tag ids",
        name="Contribution Rule Name",
        source_account_id=1,
        destination_account_id=1,
    )

    with pytest.raises(IntegrityError):
        CalculationRule.objects.create(
            tag_ids="tag ids",
            name="Contribution Rule Name",
            source_account_id=1,
            destination_account_id=1,
        )
