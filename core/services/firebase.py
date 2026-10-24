"""Lazy Firestore access for meter-reading ingestion.

The legacy implementation initialized Firebase at import time, crashing the
whole app whenever the credentials file was missing. This module initializes
on first use, fails soft (returns empty data + logs), and never blocks
application startup.
"""
from __future__ import annotations

import logging
from typing import Any

from django.conf import settings

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
        logger.exception("Firestore initialization failed; meter sync will return no data")
        return None


def fetch_meter_list() -> list[dict]:
    """Read the meter list document from Firestore.

    Returns [] on any failure — callers must tolerate empty input.
    """
    db = get_firestore_db()
    if db is None:
        return []

    try:
        doc = db.collection("meters").document("your_doc_id").get()
        if not doc.exists:
            logger.warning("Firestore document meters/your_doc_id does not exist")
            return []
        data = doc.to_dict() or {}
        meter_list = data.get("meter_list", [])
        return meter_list if isinstance(meter_list, list) else []
    except Exception:
        logger.exception("Failed to fetch meter list from Firestore")
        return []
