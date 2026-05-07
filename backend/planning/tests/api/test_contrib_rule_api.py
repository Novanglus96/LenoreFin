import pytest

AUTH = {"Authorization": "Bearer test-api-key"}

RULE_PAYLOAD = {
    "rule": "Save 10% of net",
    "cap": "5000.00",
    "order": 1,
}


@pytest.fixture
def test_contrib_rule():
    from planning.models import ContribRule

    return ContribRule.objects.create(
        rule="Existing Rule",
        cap="3000.00",
        order=0,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_create_contrib_rule(api_client):
    response = api_client.post(
        "/planning/contrib-rules/create",
        json=RULE_PAYLOAD,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_create_contrib_rule_duplicate_returns_400(api_client, test_contrib_rule):
    response = api_client.post(
        "/planning/contrib-rules/create",
        json={**RULE_PAYLOAD, "rule": test_contrib_rule.rule},
        headers=AUTH,
    )

    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_get_contrib_rule(api_client, test_contrib_rule):
    response = api_client.get(
        f"/planning/contrib-rules/get/{test_contrib_rule.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_contrib_rule.id
    assert data["rule"] == test_contrib_rule.rule


@pytest.mark.django_db
@pytest.mark.api
def test_get_contrib_rule_not_found(api_client):
    response = api_client.get("/planning/contrib-rules/get/9999", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_update_contrib_rule(api_client, test_contrib_rule):
    response = api_client.put(
        f"/planning/contrib-rules/update/{test_contrib_rule.id}",
        json={
            "rule": test_contrib_rule.rule,
            "cap": "4000.00",
            "order": 2,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_update_contrib_rule_not_found(api_client):
    response = api_client.put(
        "/planning/contrib-rules/update/9999",
        json=RULE_PAYLOAD,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_contrib_rules(api_client, test_contrib_rule):
    response = api_client.get("/planning/contrib-rules/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_list_contrib_rules_ordered_by_order(api_client):
    from planning.models import ContribRule

    ContribRule.objects.create(rule="Rule Z", order=10)
    ContribRule.objects.create(rule="Rule A", order=1)

    response = api_client.get("/planning/contrib-rules/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    orders = [item["order"] for item in data]
    assert orders == sorted(orders)


@pytest.mark.django_db
@pytest.mark.api
def test_delete_contrib_rule(api_client, test_contrib_rule):
    response = api_client.delete(
        f"/planning/contrib-rules/delete/{test_contrib_rule.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from planning.models import ContribRule

    assert not ContribRule.objects.filter(id=test_contrib_rule.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_contrib_rule_not_found(api_client):
    response = api_client.delete("/planning/contrib-rules/delete/9999", headers=AUTH)

    assert response.status_code == 404
