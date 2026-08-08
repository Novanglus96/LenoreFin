import pytest
from unittest.mock import patch, Mock
from django.contrib.auth.models import User
from administration.models import PushSubscription


AUTH = {"Authorization": "Bearer test-api-key"}


@pytest.fixture
def push_user(db):
    return User.objects.create_user(username="pushuser", password="pass")


def make_subscription(user, endpoint="https://push.example.com/sub/abc"):
    return PushSubscription.objects.create(
        user=user,
        endpoint=endpoint,
        p256dh="fakep256dh",
        auth="fakeauth",
    )


# ---------------------------------------------------------------------------
# Vapid key — no auth required, tests cleanly end-to-end
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_vapid_public_key_returns_key(api_client):
    with patch.dict("os.environ", {"VAPID_PUBLIC_KEY": "testpublickey123"}):
        response = api_client.get("/administration/push/vapid-public-key")

    assert response.status_code == 200
    assert response.json()["public_key"] == "testpublickey123"


@pytest.mark.django_db
@pytest.mark.api
def test_vapid_public_key_empty_when_not_set(api_client):
    with patch.dict("os.environ", {"VAPID_PUBLIC_KEY": ""}):
        response = api_client.get("/administration/push/vapid-public-key")

    assert response.status_code == 200
    assert response.json()["public_key"] == ""


# ---------------------------------------------------------------------------
# User-scoped endpoints
#
# The Ninja TestClient does not run Django middleware, so request.user is a
# bare Mock rather than the real User returned by authenticate().  The FK
# assignment in subscribe/unsubscribe/status therefore fails if we hit the
# real ORM.  We mock PushSubscription.objects at the view layer so we can
# still assert on response structure and that the right ORM methods are called.
# ---------------------------------------------------------------------------

@pytest.mark.django_db
@pytest.mark.api
def test_subscribe_calls_update_or_create(api_client):
    mock_sub = Mock(spec=PushSubscription)
    with patch(
        "administration.api.views.push_subscription.PushSubscription.objects.update_or_create",
        return_value=(mock_sub, True),
    ) as mock_uoc:
        response = api_client.post(
            "/administration/push/subscribe",
            json={
                "endpoint": "https://push.example.com/new",
                "p256dh": "newkey",
                "auth": "newauth",
            },
            headers=AUTH,
        )

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_uoc.assert_called_once()
    call_kwargs = mock_uoc.call_args
    assert call_kwargs.kwargs["endpoint"] == "https://push.example.com/new"
    assert call_kwargs.kwargs["defaults"]["p256dh"] == "newkey"


@pytest.mark.django_db
@pytest.mark.api
def test_unsubscribe_calls_filter_delete(api_client):
    mock_qs = Mock()
    mock_qs.delete.return_value = (1, {})
    with patch(
        "administration.api.views.push_subscription.PushSubscription.objects.filter",
        return_value=mock_qs,
    ):
        response = api_client.delete("/administration/push/unsubscribe", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_qs.delete.assert_called_once()


@pytest.mark.django_db
@pytest.mark.api
def test_status_returns_subscribed_true(api_client):
    with patch(
        "administration.api.views.push_subscription.PushSubscription.objects.filter",
    ) as mock_filter:
        mock_filter.return_value.exists.return_value = True
        response = api_client.get("/administration/push/status", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["subscribed"] is True


@pytest.mark.django_db
@pytest.mark.api
def test_status_returns_subscribed_false(api_client):
    with patch(
        "administration.api.views.push_subscription.PushSubscription.objects.filter",
    ) as mock_filter:
        mock_filter.return_value.exists.return_value = False
        response = api_client.get("/administration/push/status", headers=AUTH)

    assert response.status_code == 200
    assert response.json()["subscribed"] is False
