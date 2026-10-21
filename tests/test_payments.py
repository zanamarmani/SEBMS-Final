"""Mock payment flow — hash integrity, settlement, idempotency, scoping."""
import pytest

from core.services.payments import generate_secure_hash, to_paisa
from payment.models import Payment
from tests.factories import (
    BillFactory,
    ConsumerFactory,
    OfficeStaffUserFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def unpaid_bill():
    return BillFactory(paid=False, payableamount=700)


def _hint(bill, response_code="000", tamper_amount=None):
    amount = tamper_amount if tamper_amount is not None else to_paisa(bill.payableamount)
    ref = f"SEBMS-{bill.id}-1700000000"
    return {
        "pp_TxnRefNo": ref,
        "pp_Amount": amount,
        "pp_ResponseCode": response_code,
        "pp_SecureHash": generate_secure_hash(amount, ref),
    }


def test_initiate_returns_signed_paisa_payload(auth_for, unpaid_bill):
    consumer = unpaid_bill.meter.consumer
    client = auth_for(consumer.user)
    resp = client.post(f"/api/v1/payments/initiate/{unpaid_bill.id}/")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["amount_paisa"] == 70000
    assert data["gateway_payload"]["pp_Amount"] == 70000
    # Hash must be over the transmitted paisa value, not rupees (legacy bug).
    expected = generate_secure_hash(70000, data["gateway_payload"]["pp_TxnRefNo"])
    assert data["gateway_payload"]["pp_SecureHash"] == expected


def test_initiate_on_paid_bill_is_409(auth_for, unpaid_bill):
    unpaid_bill.paid = True
    unpaid_bill.save(update_fields=["paid"])
    consumer = unpaid_bill.meter.consumer
    client = auth_for(consumer.user)
    resp = client.post(f"/api/v1/payments/initiate/{unpaid_bill.id}/")
    assert resp.status_code == 409


def test_initiate_cannot_touch_other_consumers_bill(auth_for, unpaid_bill):
    from tests.factories import ConsumerUserFactory

    other = ConsumerUserFactory()
    client = auth_for(other)
    resp = client.post(f"/api/v1/payments/initiate/{unpaid_bill.id}/")
    assert resp.status_code == 404


def test_successful_callback_marks_bill_paid_and_records_payment(api_client, unpaid_bill):
    body = _hint(unpaid_bill)
    resp = api_client.post("/api/v1/payments/callback/", body, format="json")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "success"

    unpaid_bill.refresh_from_db()
    assert unpaid_bill.paid is True
    payment = Payment.objects.get(reference=body["pp_TxnRefNo"])
    assert payment.status == Payment.Status.SUCCESS
    assert payment.amount == unpaid_bill.payableamount


def test_duplicate_callback_is_idempotent(api_client, unpaid_bill):
    body = _hint(unpaid_bill)
    r1 = api_client.post("/api/v1/payments/callback/", body, format="json")
    r2 = api_client.post("/api/v1/payments/callback/", body, format="json")

    assert r1.status_code == 200 and r2.status_code == 200
    assert "Duplicate" in r2.json()["data"]["detail"]
    assert Payment.objects.filter(reference=body["pp_TxnRefNo"]).count() == 1
    unpaid_bill.refresh_from_db()
    assert unpaid_bill.paid is True


def test_tampered_hash_rejected(api_client, unpaid_bill):
    body = _hint(unpaid_bill)
    body["pp_SecureHash"] = "0" * 64
    resp = api_client.post("/api/v1/payments/callback/", body, format="json")
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "validation_error"
    unpaid_bill.refresh_from_db()
    assert unpaid_bill.paid is False


def test_amount_mismatch_does_not_settle(api_client, unpaid_bill):
    body = _hint(unpaid_bill, tamper_amount=1)
    resp = api_client.post("/api/v1/payments/callback/", body, format="json")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "failed"
    unpaid_bill.refresh_from_db()
    assert unpaid_bill.paid is False
    assert Payment.objects.filter(status=Payment.Status.FAILED).count() == 1


def test_declined_response_code_records_failed_payment(api_client, unpaid_bill):
    body = _hint(unpaid_bill, response_code="1001")
    resp = api_client.post("/api/v1/payments/callback/", body, format="json")
    assert resp.status_code == 200
    assert resp.json()["data"]["status"] == "failed"
    unpaid_bill.refresh_from_db()
    assert unpaid_bill.paid is False


def test_missing_callback_fields_is_400(api_client):
    resp = api_client.post("/api/v1/payments/callback/", {}, format="json")
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "validation_error"
    assert "pp_TxnRefNo" in body["error"]["details"]["missing"]


def test_payment_listing_scopes_consumer_to_own_bills(auth_for):
    mine = BillFactory(paid=True)
    Payment.objects.create(
        bill=mine, reference="SEBMS-1-1", amount=mine.payableamount,
        status=Payment.Status.SUCCESS,
    )
    other = ConsumerFactory()
    other_bill = BillFactory(meter__consumer=other, paid=True)
    Payment.objects.create(
        bill=other_bill, reference="SEBMS-2-2", amount=other_bill.payableamount,
        status=Payment.Status.SUCCESS,
    )

    client = auth_for(mine.meter.consumer.user)
    resp = client.get("/api/v1/payments/")
    assert resp.status_code == 200
    assert resp.json()["data"]["count"] == 1

    office = OfficeStaffUserFactory()
    office_client = auth_for(office)
    resp2 = office_client.get("/api/v1/payments/")
    assert resp2.status_code == 200
    assert resp2.json()["data"]["count"] == 2
