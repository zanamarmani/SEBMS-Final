"""Meter-reading ingestion and monthly bill generation.

Fixes the legacy broken pipeline (pre-migration-0003 schema references,
per-row SELECT/INSERT loops, no transactions) with a bulk, transactional,
idempotent implementation.
"""
from __future__ import annotations

import logging
from datetime import date as date_cls, datetime, timedelta
from decimal import Decimal
from typing import Any, Iterable

from django.db import transaction
from django.utils import timezone

from bill.models import Bill
from core.services.billing import (
    DUE_TERM_DAYS,
    calculate_bill_amount,
    payable_after_due_date,
)
from meterreader.models import Meter, MeterReading

logger = logging.getLogger(__name__)

# A newly registered meter starts at zero.
INITIAL_LAST_READING = Decimal("0")


def _parse_date(value: Any) -> date_cls:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date_cls):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _parse_reading(value: Any) -> int:
    return int(round(float(value)))


@transaction.atomic
def ingest_meter_data(records: Iterable[dict]) -> dict:
    """Ingest external meter-reading records (Firestore-shaped dicts).

    Idempotent on (meter, reading_date): existing pairs are skipped.
    Bulk operations only — no per-record SELECT/INSERT loops.

    Returns stats: {"fetched": n, "created": n, "skipped": n, "invalid": n}.
    """
    stats = {"fetched": 0, "created": 0, "skipped": 0, "invalid": 0}
    parsed: list[tuple[int, date_cls, int]] = []

    for record in records or []:
        stats["fetched"] += 1
        try:
            serial = int(record["serial_no"])
            reading_date = _parse_date(record["date"])
            reading = _parse_reading(record["reading"])
            parsed.append((serial, reading_date, reading))
        except (KeyError, TypeError, ValueError):
            stats["invalid"] += 1
            continue

    if not parsed:
        return stats

    serials = {serial for serial, _, _ in parsed}
    meters_by_serial: dict[int, Meter] = {
        m.meter_number: m
        for m in Meter.objects.select_for_update().filter(meter_number__in=serials).order_by("id").only("id", "meter_number")
    }

    valid = [(s, d, r) for s, d, r in parsed if s in meters_by_serial]
    stats["invalid"] += len(parsed) - len(valid)
    if not valid:
        return stats

    # Skip (meter, date) pairs that already exist — single query.
    existing_pairs = set(
        MeterReading.objects.filter(
            meter_id__in={meters_by_serial[s].id for s, _, _ in valid},
        ).values_list("meter_id", "reading_date")
    )

    latest_by_meter = {}
    for item in MeterReading.objects.filter(
        meter_id__in=[m.id for m in meters_by_serial.values()]
    ).order_by("reading_date", "id"):
        latest_by_meter[item.meter_id] = (item.reading_date, item.new_reading)

    to_create: list[MeterReading] = []
    seen_pairs: set[tuple[int, date_cls]] = set()
    for serial, reading_date, reading in sorted(valid, key=lambda item: (item[0], item[1])):
        meter = meters_by_serial[serial]
        pair = (meter.id, reading_date)
        if pair in existing_pairs or pair in seen_pairs:
            stats["skipped"] += 1
            continue
        previous_date, last = latest_by_meter.get(meter.id, (None, INITIAL_LAST_READING))
        if reading < last or (previous_date is not None and reading_date <= previous_date):
            stats["invalid"] += 1
            continue
        seen_pairs.add(pair)
        latest_by_meter[meter.id] = (reading_date, Decimal(reading))
        to_create.append(
            MeterReading(
                meter=meter,
                last_reading=last if last is not None else INITIAL_LAST_READING,
                new_reading=reading,
                reading_date=reading_date,
                processed=False,
                meter_status=True,
            )
        )

    if to_create:
        MeterReading.objects.bulk_create(to_create)
        stats["created"] = len(to_create)

    logger.info("Meter reading ingestion: %s", stats)
    return stats


@transaction.atomic
def generate_bills_for_unprocessed_readings() -> dict:
    """Bill consumption once per meter and reading month, using tariff slabs.

    Matching meters are locked to serialize imports and concurrent generation.
    Additional readings extend an unpaid monthly bill; paid bills stay intact.
    """
    bill_date = timezone.localdate()
    stats = {"processed": 0, "bills_created": 0, "bills_updated": 0, "skipped": 0}
    meter_ids = MeterReading.objects.filter(processed=False).values("meter_id")
    list(Meter.objects.select_for_update().filter(pk__in=meter_ids).order_by("pk"))
    readings = MeterReading.objects.filter(processed=False).select_related(
        "meter__consumer__consumer_tariff"
    ).order_by("meter_id", "reading_date", "id")
    groups = {}
    for reading in readings:
        consumer = reading.meter.consumer if reading.meter else None
        if (consumer is None or not consumer.approved or consumer.consumer_tariff is None
                or reading.reading_date is None or reading.new_reading is None
                or reading.last_reading is None or reading.new_reading < reading.last_reading):
            stats["skipped"] += 1
            continue
        month = reading.reading_date.replace(day=1)
        groups.setdefault((reading.meter_id, month), []).append(reading)

    for (meter_id, month), items in groups.items():
        # Month range also recognizes bills created by the legacy daily-date code.
        following_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
        existing = list(Bill.objects.filter(
            meter_id=meter_id, billmonth__gte=month, billmonth__lt=following_month
        ))
        if len(existing) > 1 or (existing and existing[0].paid):
            stats["skipped"] += len(items)
            continue
        units = sum((r.new_reading - r.last_reading for r in items), Decimal("0"))
        bill = existing[0] if existing else Bill(
            meter_id=meter_id, billmonth=month,
            duedate=bill_date + timedelta(days=DUE_TERM_DAYS),
            detectionunit=Decimal("0"), averageunit=Decimal("0"), paid=False,
        )
        if existing:
            if bill.unitsconsumed is None:
                stats["skipped"] += len(items)
                continue
            units += bill.unitsconsumed
        tariff = items[0].meter.consumer.consumer_tariff
        bill.units = bill.unitsconsumed = units
        bill.payableamount = calculate_bill_amount(units, tariff)
        bill.payable_after_due_date = payable_after_due_date(bill.payableamount)
        bill.save()
        MeterReading.objects.filter(pk__in=[r.pk for r in items]).update(processed=True)
        stats["processed"] += len(items)
        stats["bills_updated" if existing else "bills_created"] += 1

    logger.info("Bill generation complete: %s", stats)
    return stats
