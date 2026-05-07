import pytest

AUTH = {"Authorization": "Bearer test-api-key"}

RULE_PAYLOAD = {
    "tag_ids": "[]",
    "name": "Test Calc Rule",
    "source_account_id": 1,
    "destination_account_id": 2,
}


@pytest.fixture
def test_calculation_rule():
    from planning.models import CalculationRule

    return CalculationRule.objects.create(
        tag_ids="[]",
        name="Existing Rule",
        source_account_id=1,
        destination_account_id=2,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_create_calculation_rule(api_client):
    response = api_client.post(
        "/planning/calculator/calculation_rule/create",
        json=RULE_PAYLOAD,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_list_calculation_rules(api_client, test_calculation_rule):
    response = api_client.get(
        "/planning/calculator/calculation_rule/list", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    first = data[0]
    assert "id" in first
    assert "name" in first
    assert "tag_ids" in first


@pytest.mark.django_db
@pytest.mark.api
def test_list_calculation_rules_ordered_by_name(api_client):
    from planning.models import CalculationRule

    CalculationRule.objects.create(
        tag_ids="[]", name="Zebra Rule", source_account_id=1, destination_account_id=2
    )
    CalculationRule.objects.create(
        tag_ids="[]", name="Alpha Rule", source_account_id=1, destination_account_id=2
    )

    response = api_client.get(
        "/planning/calculator/calculation_rule/list", headers=AUTH
    )

    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == sorted(names)


@pytest.mark.django_db
@pytest.mark.api
def test_update_calculation_rule(api_client, test_calculation_rule):
    response = api_client.put(
        f"/planning/calculator/calculation_rule/update/{test_calculation_rule.id}",
        json={
            "tag_ids": "[1, 2]",
            "name": test_calculation_rule.name,
            "source_account_id": 3,
            "destination_account_id": 4,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_update_calculation_rule_not_found(api_client):
    response = api_client.put(
        "/planning/calculator/calculation_rule/update/9999",
        json=RULE_PAYLOAD,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_delete_calculation_rule(api_client, test_calculation_rule):
    response = api_client.delete(
        f"/planning/calculator/calculation_rule/delete/{test_calculation_rule.id}",
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from planning.models import CalculationRule

    assert not CalculationRule.objects.filter(id=test_calculation_rule.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_calculation_rule_not_found(api_client):
    response = api_client.delete(
        "/planning/calculator/calculation_rule/delete/9999", headers=AUTH
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_get_calculator_returns_structure(api_client, test_calculation_rule):
    """
    The get_calculator endpoint requires a calculation rule and returns a
    CalculatorOut with rule, transfers, and transactions fields.
    """
    response = api_client.get(
        f"/planning/calculator/get/{test_calculation_rule.id}?timeframe=30",
        headers=AUTH,
    )

    assert response.status_code == 200
    data = response.json()
    assert "rule" in data
    assert "transfers" in data
    assert "transactions" in data
    assert isinstance(data["transfers"], list)
    assert isinstance(data["transactions"], list)
    assert data["rule"]["id"] == test_calculation_rule.id


@pytest.mark.django_db
@pytest.mark.api
def test_get_calculator_not_found(api_client):
    response = api_client.get(
        "/planning/calculator/get/9999?timeframe=30", headers=AUTH
    )

    assert response.status_code == 404
