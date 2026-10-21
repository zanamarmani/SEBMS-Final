"""Meter-reader access: must be able to list meters (reading form needs ids)."""
import pytest

from tests.factories import MeterFactory, MeterReaderUserFactory

pytestmark = pytest.mark.django_db


def test_meter_reader_can_list_meters(auth_for):
    MeterFactory(meter_number=888001)
    reader = MeterReaderUserFactory()
    client = auth_for(reader)

    resp = client.get("/api/v1/meters/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["count"] >= 1
    assert all("meter_number" in m for m in body["data"]["results"])


def test_me_includes_superuser_flag_for_route_guards(auth_for):
    reader = MeterReaderUserFactory()
    client = auth_for(reader)

    data = client.get("/api/v1/auth/me/").json()["data"]
    assert data["is_superuser"] is False
    assert data["role"] == "meter_reader"
