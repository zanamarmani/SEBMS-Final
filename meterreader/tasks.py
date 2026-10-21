"""Celery tasks for the meterreader app."""
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    soft_time_limit=240,
    time_limit=300,
    acks_late=True,
)
def sync_meter_readings_firebase(self):
    """Fetch readings from Firestore and ingest them into the database.

    External IO runs off the HTTP request thread. Idempotent on
    (meter, reading_date); retried up to 3 times on transient failure.
    """
    from core.services.firebase import fetch_meter_list
    from core.services.meter_readings import ingest_meter_data

    try:
        stats = ingest_meter_data(fetch_meter_list())
        logger.info("sync_meter_readings_firebase finished: %s", stats)
        return stats
    except Exception as exc:
        logger.exception("sync_meter_readings_firebase failed")
        raise self.retry(exc=exc)
