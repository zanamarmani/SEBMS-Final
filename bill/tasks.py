"""Celery tasks for bill generation."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=300,
    time_limit=360,
    acks_late=True,
)
def generate_monthly_bills(self):
    """Generate bills for all unprocessed meter readings.

    Runs in a single transaction with bulk inserts; duplicate
    (meter, billmonth) rows are blocked by a DB unique constraint, making
    re-runs safe (at-least-once delivery).
    """
    from core.services.meter_readings import generate_bills_for_unprocessed_readings

    try:
        stats = generate_bills_for_unprocessed_readings()
        logger.info("generate_monthly_bills finished: %s", stats)
        return stats
    except Exception as exc:
        logger.exception("generate_monthly_bills failed")
        raise self.retry(exc=exc)
