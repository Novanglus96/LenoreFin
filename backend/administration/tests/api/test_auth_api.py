import pytest
from unittest.mock import patch


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.api
def test_login_success(api_client, full_access_user):
    with patch("administration.api.views.auth.authenticate", return_value=full_access_user), \
         patch("administration.api.views.auth.login"):
        response = api_client.post(
            "/auth/login",
            json={"username": "test_full_access", "password": "testpass"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_full_access"
    assert data["group"] == "full_access"


@pytest.mark.django_db
@pytest.mark.api
def test_login_readonly_user_returns_readonly_group(api_client, readonly_user):
    with patch("administration.api.views.auth.authenticate", return_value=readonly_user), \
         patch("administration.api.views.auth.login"):
        response = api_client.post(
            "/auth/login",
            json={"username": "test_readonly", "password": "testpass"},
        )
    assert response.status_code == 200
    assert response.json()["group"] == "readonly"


@pytest.mark.django_db
@pytest.mark.api
def test_login_invalid_credentials(api_client):
    with patch("administration.api.views.auth.authenticate", return_value=None):
        response = api_client.post(
            "/auth/login",
            json={"username": "nobody", "password": "wrong"},
        )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.api
def test_me_returns_full_access_user(api_client, full_access_user):
    with patch(
        "administration.api.dependencies.auth.SessionAuth.authenticate",
        return_value=full_access_user,
    ):
        response = api_client.get("/auth/me", user=full_access_user)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_full_access"
    assert data["group"] == "full_access"


@pytest.mark.django_db
@pytest.mark.api
def test_me_returns_readonly_group(api_client, readonly_user):
    with patch(
        "administration.api.dependencies.auth.SessionAuth.authenticate",
        return_value=readonly_user,
    ):
        response = api_client.get("/auth/me", user=readonly_user)
    assert response.status_code == 200
    assert response.json()["group"] == "readonly"


@pytest.mark.django_db
@pytest.mark.api
def test_me_unauthenticated(api_client):
    with patch(
        "administration.api.dependencies.auth.SessionAuth.authenticate",
        return_value=None,
    ):
        response = api_client.get("/auth/me")
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.api
def test_logout_success(api_client, full_access_user):
    with patch("administration.api.views.auth.logout") as mock_logout:
        response = api_client.post("/auth/logout", user=full_access_user)
    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_logout.assert_called_once()


@pytest.mark.django_db
@pytest.mark.api
def test_logout_unauthenticated_still_clears_session(api_client):
    """Logout with no session should still return 200 — auth=None makes it always reachable."""
    with patch("administration.api.views.auth.logout") as mock_logout:
        response = api_client.post("/auth/logout")
    assert response.status_code == 200
    mock_logout.assert_called_once()


# ---------------------------------------------------------------------------
# Permission enforcement
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@pytest.mark.api
def test_readonly_user_blocked_from_mutation(api_client, readonly_user):
    """FullAccessAuth should return 403 for readonly users."""
    from ninja.errors import HttpError

    with patch(
        "administration.api.dependencies.auth.FullAccessAuth.authenticate",
        side_effect=HttpError(403, "Read-only access: this action is not permitted"),
    ):
        response = api_client.post(
            "/transactions/create",
            json={},
        )
    assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.api
def test_unauthenticated_blocked_from_read(api_client):
    """SessionAuth should return 401 for unauthenticated requests."""
    with patch(
        "administration.api.dependencies.auth.SessionAuth.authenticate",
        return_value=None,
    ):
        response = api_client.get("/transactions/list?view_type=2")
    assert response.status_code == 401
