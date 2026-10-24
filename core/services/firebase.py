"""Lazy Firestore access for meter-reading ingestion.

The legacy implementation initialized Firebase at import time, crashing the
whole app whenever the credentials file was missing. This module initializes
on first use, fails soft (returns empty data + logs), and never blocks
application startup.
"""
from __future__ import annotations

import logging
from typing import Any

from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)

_firestore_db: Any = None
_init_failed = False


def get_firestore_db() -> Any:
    """Return the Firestore client, or None when unavailable."""
    global _firestore_db, _init_failed

    if _firestore_db is not None:
        return _firestore_db
    if _init_failed:
        return None

    try:
        from firebase_admin import firestore
        from core.services.firebase_users import get_auth_app

        _firestore_db = firestore.client(app=get_auth_app())
        logger.info("Firestore client initialized")
        return _firestore_db
    except Exception:
        _init_failed = True
        logger.error("Firestore initialization failed")
        return None


class MeterSyncUnavailable(APIException):
    status_code = 503
    default_detail = "Firebase readings could not be fetched. Please retry shortly."


def fetch_meter_list(*, strict: bool = False) -> list[dict]:
    """Read the meter list document from Firestore.

    Legacy callers receive [] on failure; manual sync uses strict=True to report errors.
    """
    db = get_firestore_db()
    if db is None:
        if strict:
            raise MeterSyncUnavailable()
        return []

    try:
        doc = db.collection("meters").document("your_doc_id").get(timeout=15, retry=None)
        if not doc.exists:
            logger.warning("Firestore document meters/your_doc_id does not exist")
            return []
        data = doc.to_dict() or {}
        meter_list = data.get("meter_list", [])
        if not isinstance(meter_list, list):
            raise ValueError("Invalid meter_list format")
        return meter_list
    except Exception:
        logger.error("Failed to fetch meter list from Firestore")
        if strict:
            raise MeterSyncUnavailable() from None
        return []
