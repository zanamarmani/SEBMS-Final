"""JWT auth flow + authorization matrix tests.

Pattern per ./prompts/modules/testing.md:
authenticated+authorized 200 / unauthenticated 401 / wrong role 403.
"""
import pytest

from tests.factories import PASSWORD, ConsumerUserFactory, SDOUserFactory

pytestmark = pytest.mark.django_db


def _login(client, email, password=PASSWORD):
    return client.post(
        "/api/v1/auth/login/", {"email": email, "password": password}, format="json"
    )


def test_login_returns_token_pair(api_client):
    user = SDOUserFactory()
    resp = _login(api_client, user.email)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "access" in body["data"] and "refresh" in body["data"]


def test_login_wrong_password_is_401(api_client):
    user = SDOUserFactory()
    resp = _login(api_client, user.email, "wrong-password")
    assert resp.status_code == 401
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "unauthenticated"


def test_refresh_rotates_and_blacklists_old_token(api_client):
    user = SDOUserFactory()
    login = _login(api_client, user.email)
    refresh1 = login.json()["data"]["refresh"]

    r1 = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh1}, format="json")
    assert r1.status_code == 200
    refresh2 = r1.json()["data"]["refresh"]
    assert refresh2 != refresh1

    # Old refresh token must now be blacklisted.
    r2 = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh1}, format="json")
    assert r2.status_code == 401


def test_logout_blacklists_refresh_token(api_client):
    user = SDOUserFactory()
    login = _login(api_client, user.email)
    refresh = login.json()["data"]["refresh"]

    out = api_client.post("/api/v1/auth/logout/", {"refresh": refresh}, format="json")
    assert out.status_code == 200

    reuse = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh}, format="json")
    assert reuse.status_code == 401


def test_unauthenticated_request_is_401(api_client):
    resp = api_client.get("/api/v1/bills/")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthenticated"


def test_consumer_forbidden_on_sdo_dashboard(auth_for):
    consumer = ConsumerUserFactory()
    client = auth_for(consumer)
    resp = client.get("/api/v1/dashboard/stats/")
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "permission_denied"


def test_sdo_allowed_on_sdo_dashboard(auth_for):
    sdo = SDOUserFactory()
    client = auth_for(sdo)
    resp = client.get("/api/v1/dashboard/stats/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "bills" in body["data"]


def test_consumer_forbidden_on_user_management(auth_for):
    consumer = ConsumerUserFactory()
    client = auth_for(consumer)
    resp = client.get("/api/v1/users/")
    assert resp.status_code == 403


def test_access_token_expires_with_short_lifetime(auth_for):
    from datetime import timedelta

    from rest_framework_simplejwt.tokens import AccessToken

    sdo = SDOUserFactory()
    token = AccessToken.for_user(sdo)
    token.set_exp(lifetime=timedelta(seconds=-1))
    client = auth_for(sdo)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.get("/api/v1/dashboard/stats/")
    assert resp.status_code == 401
