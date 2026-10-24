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
    assert reading.last_reading == 0
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


def test_first_api_reading_below_500_starts_at_zero(api_client):
    from tests.factories import MeterReaderUserFactory
    api_client.force_authenticate(MeterReaderUserFactory())
    meter = MeterFactory()
    response = api_client.post('/api/v1/meter-readings/', {
        'meter': meter.pk, 'new_reading': 50, 'reading_date': '2026-10-24',
    }, format='json')
    assert response.status_code == 201, response.content
    assert MeterReading.objects.get(meter=meter).last_reading == 0


def test_batch_readings_use_previous_value_in_date_order():
    meter = MeterFactory()
    stats = ingest_meter_data([
        _record(meter, day='2026-10-25', reading=80),
        _record(meter, day='2026-10-24', reading=50),
    ])
    assert stats['created'] == 2
    assert list(MeterReading.objects.filter(meter=meter).order_by('reading_date').values_list('last_reading', 'new_reading')) == [(0, 50), (50, 80)]


def test_sync_rejects_decreasing_and_backdated_readings():
    meter = MeterFactory()
    ingest_meter_data([_record(meter, day='2026-10-24', reading=50)])
    stats = ingest_meter_data([
        _record(meter, day='2026-10-25', reading=40),
        _record(meter, day='2026-10-23', reading=30),
    ])
    assert stats['invalid'] == 2
    assert stats['created'] == 0


def test_reset_only_unbilled_initial_legacy_baseline():
    import importlib
    from django.apps import apps
    from tests.factories import MeterReadingFactory, BillFactory
    first = MeterReadingFactory(last_reading=500, new_reading=50, reading_date=datetime.date(2026, 10, 24))
    next_reading = MeterReadingFactory(meter=first.meter, last_reading=50, new_reading=80, reading_date=datetime.date(2026, 10, 25))
    billed = MeterReadingFactory(last_reading=500, new_reading=700)
    BillFactory(meter=billed.meter, paid=True)
    processed = MeterReadingFactory(last_reading=500, processed=True)
    migration = importlib.import_module('meterreader.migrations.0010_fix_unbilled_initial_baselines')
    migration.reset_unbilled_initial_baselines(apps, None)
    for r in (first, next_reading, billed, processed):
        r.refresh_from_db()
    assert first.last_reading == 0
    assert next_reading.last_reading == 50
    assert billed.last_reading == 500
    assert processed.last_reading == 500
