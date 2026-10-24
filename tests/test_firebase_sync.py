from unittest.mock import MagicMock, patch

import pytest

from core.services.firebase import MeterSyncUnavailable, fetch_meter_list
from meterreader.models import MeterReading
from tests.factories import MeterFactory, MeterReaderUserFactory, SDOUserFactory

pytestmark = pytest.mark.django_db


def test_sync_imports_and_repeat_skips_without_broker(api_client):
    api_client.force_authenticate(SDOUserFactory())
    meter = MeterFactory()
    records = [{"serial_no": meter.meter_number, "date": "2026-10-24", "reading": 900}]
    with patch("meterreader.views.fetch_meter_list", return_value=records), patch("meterreader.tasks.sync_meter_readings_firebase.delay") as enqueue:
        first = api_client.post("/api/v1/meter-readings/sync/")
        second = api_client.post("/api/v1/meter-readings/sync/")
    assert first.status_code == 200
    assert first.json()["data"] == {"status": "COMPLETED", "fetched": 1, "created": 1, "skipped": 0, "invalid": 0}
    assert second.json()["data"]["skipped"] == 1
    assert MeterReading.objects.count() == 1
    enqueue.assert_not_called()


def test_sync_provider_failure_is_not_empty_success(api_client):
    api_client.force_authenticate(SDOUserFactory())
    with patch("meterreader.views.fetch_meter_list", side_effect=MeterSyncUnavailable()):
        response = api_client.post("/api/v1/meter-readings/sync/")
    assert response.status_code == 503
    assert not MeterReading.objects.exists()


def test_reader_cannot_start_office_sync(api_client):
    api_client.force_authenticate(MeterReaderUserFactory())
    with patch("meterreader.views.fetch_meter_list") as fetch:
        response = api_client.post("/api/v1/meter-readings/sync/")
    assert response.status_code == 403
    fetch.assert_not_called()


def test_strict_fetch_failure_and_timeout():
    db = MagicMock()
    db.collection.return_value.document.return_value.get.side_effect = RuntimeError("unavailable")
    with patch("core.services.firebase.get_firestore_db", return_value=db):
        with pytest.raises(MeterSyncUnavailable):
            fetch_meter_list(strict=True)
    db.collection.return_value.document.return_value.get.assert_called_once_with(timeout=15, retry=None)


def test_empty_firebase_document_is_valid():
    db = MagicMock()
    db.collection.return_value.document.return_value.get.return_value.to_dict.return_value = {"meter_list": []}
    with patch("core.services.firebase.get_firestore_db", return_value=db):
        assert fetch_meter_list(strict=True) == []
