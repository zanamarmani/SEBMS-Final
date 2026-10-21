"""Regression tests: tariff & consumer listing (both returned 500 pre-fix)."""
import pytest

from tests.factories import (
    ConsumerFactory,
    OfficeStaffUserFactory,
    SDOUserFactory,
    TariffFactory,
)

pytestmark = pytest.mark.django_db


def test_tariff_list_for_any_authenticated_user(auth_for):
    TariffFactory(tariff_type="domestic", price_100=3)
    TariffFactory(tariff_type="commercial", price_100=9)
    sdo = SDOUserFactory()
    client = auth_for(sdo)

    resp = client.get("/api/v1/tariffs/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["count"] == 2
    types = {t["tariff_type"] for t in body["data"]["results"]}
    assert types == {"domestic", "commercial"}


def test_consumer_list_for_office_staff(auth_for):
    ConsumerFactory(consumer_number="C555001")
    ConsumerFactory(consumer_number="C555002")
    office = OfficeStaffUserFactory()
    client = auth_for(office)

    resp = client.get("/api/v1/consumers/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["data"]["count"] == 2
    # Nested tariff must serialize without extra queries breaking the row.
    first = body["data"]["results"][0]
    assert first["consumer_tariff_detail"]["tariff_type"]


def test_consumer_list_includes_meters_prefetch(auth_for):
    from tests.factories import MeterFactory

    consumer = ConsumerFactory()
    MeterFactory(consumer=consumer, meter_number=777001)
    office = OfficeStaffUserFactory()
    client = auth_for(office)

    resp = client.get("/api/v1/consumers/")
    assert resp.status_code == 200
    row = resp.json()["data"]["results"][0]
    assert row["meter_numbers"] == [777001]


def test_sdo_can_create_and_update_tariff(auth_for):
    sdo = SDOUserFactory()
    client = auth_for(sdo)

    create = client.post(
        "/api/v1/tariffs/",
        {
            "tariff_type": "industrial",
            "price_100": 5,
            "price_200": 7,
            "price_300": 9,
            "price_above": 12,
        },
        format="json",
    )
    assert create.status_code == 201
    tariff_id = create.json()["data"]["id"]

    dup = client.post(
        "/api/v1/tariffs/",
        {"tariff_type": "industrial", "price_100": 5},
        format="json",
    )
    assert dup.status_code == 400

    patch = client.patch(
        f"/api/v1/tariffs/{tariff_id}/", {"price_above": 15}, format="json"
    )
    assert patch.status_code == 200
    assert patch.json()["data"]["price_above"] == "15.00"


def test_consumer_role_cannot_create_tariff(auth_for):
    from tests.factories import ConsumerUserFactory

    user = ConsumerUserFactory()
    client = auth_for(user)
    resp = client.post(
        "/api/v1/tariffs/",
        {"tariff_type": "industrial", "price_100": 5},
        format="json",
    )
    assert resp.status_code == 403
