"""Bill generation service + API scoping + N+1 regression test."""
import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from bill.models import Bill
from core.services.meter_readings import generate_bills_for_unprocessed_readings
from tests.factories import (
    BillFactory,
    ConsumerFactory,
    MeterFactory,
    MeterReadingFactory,
    OfficeStaffUserFactory,
    UnapprovedConsumerFactory,
)

pytestmark = pytest.mark.django_db


def test_generate_bills_creates_bills_and_marks_readings_processed():
    reading = MeterReadingFactory(last_reading=500, new_reading=700, processed=False)

    stats = generate_bills_for_unprocessed_readings()

    assert stats["bills_created"] == 1
    bill = Bill.objects.get()
    assert bill.meter == reading.meter
    assert bill.unitsconsumed == 200
    # 100*3 + 100*4
    assert bill.payableamount == 700
    assert bill.payable_after_due_date == 770
    assert bill.paid is False

    reading.refresh_from_db()
    assert reading.processed is True


def test_generate_bills_skips_unapproved_consumers():
    meter = MeterFactory(consumer=UnapprovedConsumerFactory())
    MeterReadingFactory(meter=meter, processed=False)

    stats = generate_bills_for_unprocessed_readings()

    assert stats["bills_created"] == 0
    assert stats["skipped"] == 1
    assert Bill.objects.count() == 0


def test_generate_bills_is_idempotent_on_rerun():
    MeterReadingFactory(processed=False)
    generate_bills_for_unprocessed_readings()
    assert Bill.objects.count() == 1

    stats = generate_bills_for_unprocessed_readings()
    assert stats["bills_created"] == 0
    assert Bill.objects.count() == 1


def test_generate_endpoint_accepted_and_runs_task(auth_for):
    MeterReadingFactory(processed=False)
    office = OfficeStaffUserFactory()
    client = auth_for(office)

    resp = client.post("/api/v1/bills/generate/")
    assert resp.status_code == 202
    assert "task_id" in resp.json()["data"]
    assert Bill.objects.count() == 1  # eager mode executed the task


def test_consumer_sees_only_own_bills(auth_for):
    mine = BillFactory()
    other = ConsumerFactory()
    BillFactory(meter__consumer=other)

    client = auth_for(mine.meter.consumer.user)
    resp = client.get("/api/v1/bills/")
    assert resp.status_code == 200
    results = resp.json()["data"]["results"]
    assert len(results) == 1
    assert results[0]["id"] == mine.id


def test_office_staff_sees_all_bills(auth_for):
    BillFactory()
    BillFactory()
    office = OfficeStaffUserFactory()
    client = auth_for(office)
    resp = client.get("/api/v1/bills/")
    assert resp.status_code == 200
    # Bills use cursor pagination: results + next/previous, no count.
    assert len(resp.json()["data"]["results"]) == 2


def test_bill_list_query_count_constant_as_rows_grow(auth_for):
    """ORM regression guard: query count must not grow with result size."""
    office = OfficeStaffUserFactory()
    client = auth_for(office)

    for _ in range(3):
        BillFactory()
    with CaptureQueriesContext(connection) as first:
        r1 = client.get("/api/v1/bills/")
    assert r1.status_code == 200

    for _ in range(7):
        BillFactory()
    with CaptureQueriesContext(connection) as second:
        r2 = client.get("/api/v1/bills/")
    assert r2.status_code == 200

    assert len(second.captured_queries) == len(first.captured_queries), (
        f"N+1 detected: {len(first.captured_queries)} queries for 3 rows vs "
        f"{len(second.captured_queries)} queries for 10 rows"
    )
