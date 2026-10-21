"""Tests for SPA-support endpoints: /auth/me/ + public tariff reads."""
import pytest

from tests.factories import SDOUserFactory, TariffFactory

pytestmark = pytest.mark.django_db


def test_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/auth/me/")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "unauthenticated"


def test_me_returns_identity_and_role(auth_for):
    sdo = SDOUserFactory(email="me-sdo@sebms.dev")
    client = auth_for(sdo)

    resp = client.get("/api/v1/auth/me/")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["email"] == "me-sdo@sebms.dev"
    assert data["role"] == "sdo"
    assert data["is_active"] is True


def test_tariff_list_is_public_for_registration(api_client):
    TariffFactory(tariff_type="domestic", price_100=3)

    resp = api_client.get("/api/v1/tariffs/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["data"]["count"] == 1


def test_tariff_writes_still_sdo_only(api_client):
    resp = api_client.post(
        "/api/v1/tariffs/", {"tariff_type": "domestic", "price_100": 3}, format="json"
    )
    assert resp.status_code == 401
