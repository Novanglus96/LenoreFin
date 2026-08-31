import pytest

AUTH = {"Authorization": "Bearer test-api-key"}

BUCKET_PAYLOAD = {
    "name": "Test 401k",
    "contribution_per_paycheck": "100.00",
    "minimum_per_paycheck": "50.00",
    "active": True,
}


@pytest.fixture
def test_bucket():
    from planning.models import Bucket

    return Bucket.objects.create(
        name="Existing 401k",
        contribution_per_paycheck=200.00,
        minimum_per_paycheck=100.00,
        target_balance=10000.00,
        active=True,
    )


@pytest.mark.django_db
@pytest.mark.api
def test_create_bucket(api_client):
    response = api_client.post(
        "/planning/buckets/create",
        json=BUCKET_PAYLOAD,
        headers=AUTH,
    )

    assert response.status_code == 200
    assert "id" in response.json()


@pytest.mark.django_db
@pytest.mark.api
def test_create_bucket_duplicate_returns_400(api_client, test_bucket):
    response = api_client.post(
        "/planning/buckets/create",
        json={**BUCKET_PAYLOAD, "name": test_bucket.name},
        headers=AUTH,
    )

    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_get_bucket(api_client, test_bucket):
    response = api_client.get(
        f"/planning/buckets/get/{test_bucket.id}", headers=AUTH
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_bucket.id
    assert data["name"] == test_bucket.name


@pytest.mark.django_db
@pytest.mark.api
def test_get_bucket_not_found(api_client):
    response = api_client.get("/planning/buckets/get/9999", headers=AUTH)

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_update_bucket(api_client, test_bucket):
    response = api_client.put(
        f"/planning/buckets/update/{test_bucket.id}",
        json={
            "name": test_bucket.name,
            "contribution_per_paycheck": "150.00",
            "minimum_per_paycheck": "75.00",
                    "active": True,
        },
        headers=AUTH,
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_update_bucket_not_found(api_client):
    response = api_client.put(
        "/planning/buckets/update/9999",
        json=BUCKET_PAYLOAD,
        headers=AUTH,
    )

    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.api
def test_list_buckets_returns_structure(api_client, test_bucket):
    response = api_client.get("/planning/buckets/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    assert "buckets" in data
    assert "per_paycheck_total" in data
    assert "emergency_paycheck_total" in data
    assert "total_emergency" in data
    assert isinstance(data["buckets"], list)
    assert len(data["buckets"]) >= 1


@pytest.mark.django_db
@pytest.mark.api
def test_list_buckets_totals_sum_active(api_client):
    from planning.models import Bucket

    Bucket.objects.create(
        name="Active A",
        contribution_per_paycheck=100.00,
        minimum_per_paycheck=50.00,
        target_balance=5000.00,
        active=True,
    )
    Bucket.objects.create(
        name="Inactive B",
        contribution_per_paycheck=999.00,
        minimum_per_paycheck=999.00,
        target_balance=9999.00,
        active=False,
    )

    response = api_client.get("/planning/buckets/list", headers=AUTH)

    assert response.status_code == 200
    data = response.json()
    # Totals should only count active buckets
    assert float(data["per_paycheck_total"]) == 100.00


@pytest.mark.django_db
@pytest.mark.api
def test_delete_bucket(api_client, test_bucket):
    response = api_client.delete(
        f"/planning/buckets/delete/{test_bucket.id}", headers=AUTH
    )

    assert response.status_code == 200
    assert response.json()["success"] is True

    from planning.models import Bucket

    assert not Bucket.objects.filter(id=test_bucket.id).exists()


@pytest.mark.django_db
@pytest.mark.api
def test_delete_bucket_not_found(api_client):
    response = api_client.delete("/planning/buckets/delete/9999", headers=AUTH)

    assert response.status_code == 404
