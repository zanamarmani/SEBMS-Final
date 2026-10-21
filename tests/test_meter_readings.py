"""Meter-reading ingestion (Firestore-shaped records) tests."""
import datetime

import pytest

from core.services.meter_readings import ingest_meter_data
from meterreader.models import MeterReading
from tests.factories import MeterFactory

pytestmark = pytest.mark.django_db


def _record(meter, day="2026-02-01", reading=1500):
    return {"serial_no": meter.meter_number, "date": day, "reading": reading}


def test_ingest_creates_readings_with_derived_last_reading():
    meter = MeterFactory()

    stats = ingest_meter_data([_record(meter)])

    assert stats == {"fetched": 1, "created": 1, "skipped": 0, "invalid": 0}
    reading = MeterReading.objects.get()
    assert reading.last_reading == 500  # legacy initial default
    assert reading.new_reading == 1500
    assert reading.processed is False


def test_ingest_second_run_is_idempotent():
    meter = MeterFactory()
    ingest_meter_data([_record(meter)])
    stats = ingest_meter_data([_record(meter)])

    assert stats["created"] == 0
    assert stats["skipped"] == 1
    assert MeterReading.objects.count() == 1


def test_ingest_uses_previous_reading_on_next_day():
    meter = MeterFactory()
    ingest_meter_data([_record(meter, day="2026-02-01", reading=1500)])
    ingest_meter_data([_record(meter, day="2026-02-02", reading=1700)])

    latest = MeterReading.objects.latest("reading_date")
    assert latest.last_reading == 1500
    assert latest.new_reading == 1700


def test_ingest_counts_invalid_and_unknown_meters():
    known = MeterFactory()
    stats = ingest_meter_data(
        [
            {"serial_no": known.meter_number, "date": "2026-02-01", "reading": 900},
            {"serial_no": 999999999, "date": "2026-02-01", "reading": 900},
            {"date": "2026-02-01", "reading": 900},  # missing serial
            {"serial_no": known.meter_number, "date": "not-a-date", "reading": 900},
        ]
    )
    assert stats["created"] == 1
    assert stats["invalid"] == 3


def test_reading_create_rejects_negative_consumption(auth_for):
    from tests.factories import MeterReaderUserFactory

    meter = MeterFactory()
    MeterReading.objects.create(
        meter=meter, last_reading=500, new_reading=800,
        reading_date=datetime.date(2026, 3, 1), processed=True,
    )
    client = auth_for(MeterReaderUserFactory())
    resp = client.post(
        "/api/v1/meter-readings/",
        {
            "meter": meter.id,
            "new_reading": 700,
            "reading_date": "2026-03-02",
        },
        format="json",
    )
    assert resp.status_code == 400
    assert "new_reading" in resp.json()["error"]["details"]
