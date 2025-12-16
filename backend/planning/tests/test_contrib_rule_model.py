import pytest
from planning.models import ContribRule


@pytest.mark.django_db
def test_contrib_rule_creation():
    contrib_rule = ContribRule.objects.create(
        rule="Contrib Rule", cap="Cap", order=1
    )

    assert contrib_rule.id is not None
    assert contrib_rule.rule == "Contrib Rule"
    assert contrib_rule.cap == "Cap"
    assert contrib_rule.order == 1


@pytest.mark.django_db
def test_contrib_rule_defaults():
    contrib_rule = ContribRule.objects.create(rule="Contrib Rule")

    assert contrib_rule.id is not None
    assert contrib_rule.cap is None
    assert contrib_rule.order == 0


@pytest.mark.django_db
def test_contrib_rule_string_representation():
    contrib_rule = ContribRule.objects.create(rule="Contrib Rule")
    expected = "Contrib Rule"

    assert str(contrib_rule) == expected
