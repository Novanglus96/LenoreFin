from decimal import Decimal as D

import pytest

from planning.models import Bucket, WindfallRule

AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.mark.django_db
@pytest.mark.api
def test_bucket_crud_takes_the_account_from_the_reminder(api_client, test_reminder, test_savings_account):
    created = api_client.post(
        "/planning/buckets/create",
        json={"name": "Pet", "contribution_per_paycheck": "60.00", "reminder_id": test_reminder.pk,
              "goal_amount": "500.00"},
        headers=AUTH,
    )
    assert created.status_code == 200
    bucket = Bucket.objects.get(pk=created.json()["id"])
    assert bucket.account == test_savings_account

    listed = api_client.get("/planning/buckets/list", headers=AUTH).json()
    assert listed[0]["account_name"] == test_savings_account.account_name
    assert listed[0]["reminder_amount"] == "1.00"

    bad = api_client.put(
        f"/planning/buckets/update/{bucket.pk}",
        json={"name": "Pet", "contribution_per_paycheck": "-1"},
        headers=AUTH,
    )
    assert bad.status_code == 400

    api_client.put(
        f"/planning/buckets/update/{bucket.pk}",
        json={"name": "Pets", "contribution_per_paycheck": "70", "account_id": test_savings_account.pk},
        headers=AUTH,
    )
    bucket.refresh_from_db()
    assert (bucket.name, bucket.contribution_per_paycheck, bucket.goal_amount) == ("Pets", D("70"), None)

    assert api_client.delete(f"/planning/buckets/delete/{bucket.pk}", headers=AUTH).status_code == 200
    assert not Bucket.objects.exists()


@pytest.mark.django_db
@pytest.mark.api
def test_reminder_into_another_account_is_refused(api_client, test_reminder, test_checking_account):
    response = api_client.post(
        "/planning/buckets/create",
        json={"name": "Pet", "reminder_id": test_reminder.pk, "account_id": test_checking_account.pk},
        headers=AUTH,
    )
    assert response.status_code == 400


@pytest.mark.django_db
@pytest.mark.api
def test_windfall_rule_crud(api_client):
    bucket = Bucket.objects.create(name="Car")
    created = api_client.post(
        "/planning/windfall-rules/create",
        json={"rule": "Car first", "bucket_id": bucket.pk, "cap_amount": "300", "order": 1},
        headers=AUTH,
    ).json()
    rules = api_client.get("/planning/windfall-rules/list", headers=AUTH).json()
    assert rules[0]["bucket_name"] == "Car" and rules[0]["cap_amount"] == "300.00"
    api_client.delete(f"/planning/windfall-rules/delete/{created['id']}", headers=AUTH)
    assert not WindfallRule.objects.exists()


@pytest.mark.django_db
@pytest.mark.api
def test_plan_without_a_funding_account_says_why(api_client):
    response = api_client.get("/planning/savings-plan/", headers=AUTH)
    assert response.status_code == 400
