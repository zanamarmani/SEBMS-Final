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
from django.db.models import Max
from django.utils import timezone

from bill.models import Bill
from core.services.billing import (
    DUE_TERM_DAYS,
    calculate_bill_amount,
    payable_after_due_date,
)
from meterreader.models import Meter, MeterReading

logger = logging.getLogger(__name__)

# Legacy default applied when a meter has no prior reading.
INITIAL_LAST_READING = Decimal("500")


def _parse_date(value: Any) -> date_cls:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date_cls):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def _parse_reading(value: Any) -> int:
    return int(round(float(value)))


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
        for m in Meter.objects.filter(meter_number__in=serials).only("id", "meter_number")
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

    # Latest prior reading per meter — single query.
    latest_by_meter: dict[int, Decimal] = dict(
        MeterReading.objects.filter(
            meter_id__in={meters_by_serial[s].id for s, _, _ in valid}
        )
        .values("meter_id")
        .annotate(latest=Max("new_reading"))
        .values_list("meter_id", "latest")
    )

    to_create: list[MeterReading] = []
    seen_pairs: set[tuple[int, date_cls]] = set()
    for serial, reading_date, reading in valid:
        meter = meters_by_serial[serial]
        pair = (meter.id, reading_date)
        if pair in existing_pairs or pair in seen_pairs:
            stats["skipped"] += 1
            continue
        seen_pairs.add(pair)
        last = latest_by_meter.get(meter.id)
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


def generate_bills_for_unprocessed_readings() -> dict:
    """Generate bills for every unprocessed meter reading.

    Corrects the legacy implementation which queried fields removed in
    migration 0003 (Meter.processed / Meter.new_reading). Runs in a single
    transaction with bulk_create + bulk_update; duplicate bills for the same
    (meter, billmonth) are blocked by a DB unique constraint.
    """
    bill_date = timezone.localdate()
    duedate = bill_date + timedelta(days=DUE_TERM_DAYS)
    stats = {"processed": 0, "bills_created": 0, "skipped": 0}

    readings = (
        MeterReading.objects.filter(processed=False)
        .select_related("meter__consumer__consumer_tariff")
        .order_by("id")
    )

    bills: list[Bill] = []
    to_mark: list[MeterReading] = []

    for reading in readings:
        consumer = reading.meter.consumer if reading.meter else None
        if consumer is None or not consumer.approved:
            stats["skipped"] += 1
            continue

        tariff = consumer.consumer_tariff
        if tariff is None:
            logger.warning(
                "No tariff for consumer %s; skipping reading %s",
                consumer.id,
                reading.id,
            )
            stats["skipped"] += 1
            continue

        units_consumed = Decimal(reading.new_reading) - Decimal(reading.last_reading)
        if units_consumed < 0:
            logger.warning(
                "Negative consumption on reading %s (new=%s last=%s); skipping",
                reading.id,
                reading.new_reading,
                reading.last_reading,
            )
            stats["skipped"] += 1
            continue

        payable = calculate_bill_amount(units_consumed, tariff)
        bills.append(
            Bill(
                billmonth=bill_date,
                duedate=duedate,
                detectionunit=Decimal("0.00"),
                averageunit=Decimal("0.00"),
                units=units_consumed,
                unitsconsumed=units_consumed,
                payableamount=payable,
                payable_after_due_date=payable_after_due_date(payable),
                meter=reading.meter,
                paid=False,
            )
        )
        to_mark.append(reading)
        stats["processed"] += 1

    if bills:
        try:
            with transaction.atomic():
                created = Bill.objects.bulk_create(bills)
                MeterReading.objects.filter(
                    id__in=[r.id for r in to_mark]
                ).update(processed=True)
                stats["bills_created"] = len(created)
        except Exception:
            logger.exception("Bill generation failed; transaction rolled back")
            raise

    logger.info("Bill generation complete: %s", stats)
    return stats
