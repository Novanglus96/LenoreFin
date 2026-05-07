import pytest

AUTH = {"Authorization": "Bearer test-api-key"}

CONTRIB_PAYLOAD = {
    "contribution": "Test 401k",
    "per_paycheck": "100.00",
    "emergency_amt": "50.00",
    "emergency_diff": "50.00",
    "cap": "5000.00",
    "active": True,
}


@pytest.fixture
def test_contribution():
    from planning.models import Contribution

    return Contribution.objects.create(
        contribution="Existing 401k",
        per_paycheck=200.00,
        emergency_amt=100.00,
        emergency_diff=100.00,
        cap=10000.00,
        active=True,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_create_contribution(api_client):
    response = api_client.post(
        "/planning/contributions/create",
        json=CONTRIB_PAYLOAD,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_create_contribution_duplicate_returns_400(api_client, test_contribution):
    response = api_client.post(
        "/planning/contributions/create",
        json={**CONTRIB_PAYLOAD, "contribution": test_contribution.contribution},
        headers=AUTH,
    )

    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_get_contribution(api_client, test_contribution):
    response = api_client.get(
        f"/planning/contributions/get/{test_contribution.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_contribution.id
    assert data["contribution"] == test_contribution.contribution


@pytest.mark.django_db
@pytest.mark.api
def test_get_contribution_not_found(api_client):
    response = api_client.get("/planning/contributions/get/9999", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_update_contribution(api_client, test_contribution):
    response = api_client.put(
        f"/planning/contributions/update/{test_contribution.id}",
        json={
            "contribution": test_contribution.contribution,
            "per_paycheck": "150.00",
            "emergency_amt": "75.00",
            "emergency_diff": "75.00",
            "cap": "5000.00",
            "active": True,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_update_contribution_not_found(api_client):
    response = api_client.put(
        "/planning/contributions/update/9999",
        json=CONTRIB_PAYLOAD,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_contributions_returns_structure(api_client, test_contribution):
    response = api_client.get("/planning/contributions/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert "contributions" in data
    assert "per_paycheck_total" in data
    assert "emergency_paycheck_total" in data
    assert "total_emergency" in data
    assert isinstance(data["contributions"], list)
    assert len(data["contributions"]) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_list_contributions_totals_sum_active(api_client):
    from planning.models import Contribution

    Contribution.objects.create(
        contribution="Active A",
        per_paycheck=100.00,
        emergency_amt=50.00,
        emergency_diff=50.00,
        cap=5000.00,
        active=True,
    )
    Contribution.objects.create(
        contribution="Inactive B",
        per_paycheck=999.00,
        emergency_amt=999.00,
        emergency_diff=999.00,
        cap=9999.00,
        active=False,
    )

    response = api_client.get("/planning/contributions/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    # Totals should only count active contributions
    assert float(data["per_paycheck_total"]) == 100.00


@pytest.mark.django_db
@pytest.mark.api
def test_delete_contribution(api_client, test_contribution):
    response = api_client.delete(
        f"/planning/contributions/delete/{test_contribution.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from planning.models import Contribution

    assert not Contribution.objects.filter(id=test_contribution.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_contribution_not_found(api_client):
    response = api_client.delete("/planning/contributions/delete/9999", headers=AUTH)

    assert response.status_code == 404
