"""JazzCash payment orchestration (mock mode by default).

Fixes the legacy flow:
- Hash is computed over the SAME amount value that is transmitted (paisa),
  not rupees (legacy bug: gateway rejected every request).
- The callback endpoint verifies the secure hash and amount, then marks the
  bill paid and records the Payment inside one transaction (legacy handler
  was a stub that never updated anything).
- Duplicate callbacks are idempotent: the unique Payment.reference plus the
  Bill.paid check guarantee a bill can only be credited once.
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import re
from decimal import Decimal
from typing import Any

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from bill.models import Bill
from payment.models import Payment

logger = logging.getLogger(__name__)

REF_PATTERN = re.compile(r"^SEBMS-(?P<bill_id>\d+)-(?P<ts>\d+)$")


def generate_secure_hash(amount_paisa: str, txn_ref_no: str) -> str:
    """JazzCash-style SHA-256 over merchant creds + amount(paisa) + ref + salt."""
    raw = ":".join(
        [
            settings.JAZZCASH_MERCHANT_ID,
            settings.JAZZCASH_PASSWORD,
            str(amount_paisa),
            str(txn_ref_no),
            settings.JAZZCASH_INTEGRITY_SALT,
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def to_paisa(amount: Decimal) -> int:
    return int(Decimal(amount) * 100)


def initiate_payment(bill: Bill) -> dict[str, Any]:
    """Build a payment-initiation payload for the (mock) gateway."""
    if bill.paid:
        raise ValueError("Bill is already paid.")

    amount_paisa = to_paisa(bill.payableamount)
    txn_ref_no = f"SEBMS-{bill.id}-{int(timezone.now().timestamp())}"
    secure_hash = generate_secure_hash(amount_paisa, txn_ref_no)

    return {
        "mode": settings.JAZZCASH_MODE,
        "gateway_url": settings.JAZZCASH_GATEWAY_URL,
        "bill_id": bill.id,
        "bill_amount": str(bill.payableamount),
        "amount_paisa": amount_paisa,
        "gateway_payload": {
            "pp_MerchantID": settings.JAZZCASH_MERCHANT_ID,
            "pp_Password": settings.JAZZCASH_PASSWORD,
            "pp_Amount": amount_paisa,
            "pp_TxnRefNo": txn_ref_no,
            "pp_Description": f"Bill Payment #{bill.id}",
            "pp_SecureHash": secure_hash,
        },
        "mock_callback_hint": {
            "endpoint": "/api/v1/payments/callback/",
            "body": {
                "pp_TxnRefNo": txn_ref_no,
                "pp_Amount": amount_paisa,
                "pp_ResponseCode": "000",
                "pp_SecureHash": secure_hash,
            },
        },
    }


@transaction.atomic
def process_payment_callback(
    txn_ref_no: str,
    amount_paisa: int,
    response_code: str,
    secure_hash: str,
) -> dict[str, Any]:
    """Verify and settle a gateway callback (idempotent).

    Returns a result dict: {"status": "success"|"failed", "payment_id": ...,
    "bill_id": ..., "detail": ...}. Raises ValueError on signature mismatch.
    """
    expected_hash = generate_secure_hash(amount_paisa, txn_ref_no)
    if not hmac.compare_digest(expected_hash, secure_hash.lower()):
        raise ValueError("Invalid secure hash for this transaction.")

    match = REF_PATTERN.match(txn_ref_no)
    if not match:
        raise ValueError("Malformed transaction reference.")

    bill_id = int(match.group("bill_id"))
    # select_for_update cannot join nullable relations (Postgres), so lock the
    # Bill row alone; meter/consumer are not mutated by settlement.
    bill = Bill.objects.select_for_update().filter(id=bill_id).first()
    if bill is None:
        raise ValueError("Bill not found for this transaction.")

    # Idempotent replay: already-successful payment for this reference.
    existing = Payment.objects.filter(reference=txn_ref_no, status=Payment.Status.SUCCESS).first()
    if existing is not None:
        return {
            "status": "success",
            "payment_id": existing.id,
            "bill_id": bill.id,
            "detail": "Duplicate callback ignored; bill already settled.",
        }

    if response_code != "000":
        payment = Payment.objects.create(
            bill=bill,
            reference=txn_ref_no,
            amount=Decimal(amount_paisa) / 100,
            bank_charges=Decimal("0.00"),
            arrears_charges=Decimal("0.00"),
            status=Payment.Status.FAILED,
        )
        return {
            "status": "failed",
            "payment_id": payment.id,
            "bill_id": bill.id,
            "detail": f"Gateway declined with response code {response_code}.",
        }

    expected_paisa = to_paisa(bill.payableamount)
    if int(amount_paisa) != expected_paisa:
        payment = Payment.objects.create(
            bill=bill,
            reference=txn_ref_no,
            amount=Decimal(amount_paisa) / 100,
            bank_charges=Decimal("0.00"),
            arrears_charges=Decimal("0.00"),
            status=Payment.Status.FAILED,
        )
        return {
            "status": "failed",
            "payment_id": payment.id,
            "bill_id": bill.id,
            "detail": "Amount mismatch; bill not marked paid.",
        }

    payment, _created = Payment.objects.get_or_create(
        reference=txn_ref_no,
        defaults={
            "bill": bill,
            "amount": bill.payableamount,
            "bank_charges": Decimal("0.00"),
            "arrears_charges": Decimal("0.00"),
            "status": Payment.Status.SUCCESS,
        },
    )
    if not bill.paid:
        bill.paid = True
        bill.save(update_fields=["paid"])

    logger.info("Payment settled: bill=%s ref=%s amount=%s", bill.id, txn_ref_no, amount_paisa)
    return {
        "status": "success",
        "payment_id": payment.id,
        "bill_id": bill.id,
        "detail": "Payment verified and bill marked paid.",
    }
