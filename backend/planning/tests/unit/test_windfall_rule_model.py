import pytest
from planning.models import WindfallRule


@pytest.mark.django_db
def test_windfall_rule_creation():
    windfall_rule = WindfallRule.objects.create(
        rule="Windfall Rule", cap="Cap", order=1
    )

    assert windfall_rule.id is not None
    assert windfall_rule.rule == "Windfall Rule"
    assert windfall_rule.cap == "Cap"
    assert windfall_rule.order == 1


@pytest.mark.django_db
def test_windfall_rule_defaults():
    windfall_rule = WindfallRule.objects.create(rule="Windfall Rule")

    assert windfall_rule.id is not None
    assert windfall_rule.cap is None
    assert windfall_rule.order == 0


@pytest.mark.django_db
def test_windfall_rule_string_representation():
    windfall_rule = WindfallRule.objects.create(rule="Windfall Rule")
    expected = "Windfall Rule"

    assert str(windfall_rule) == expected
