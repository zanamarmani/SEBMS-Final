"""Consumer registration + SDO approval workflow tests."""
import pytest

from consumer.models import Consumer
from tests.factories import ConsumerUserFactory, SDOUserFactory, UnapprovedConsumerFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def tariff(db):
    from tests.factories import TariffFactory

    return TariffFactory()


def test_public_registration_creates_unapproved_consumer(api_client, tariff):
    resp = api_client.post(
        "/api/v1/consumers/register/",
        {
            "email": "reg@consumer.test",
            "password": "An0therStr0ng!",
            "consumer_number": "C888001",
            "consumer_name": "New Consumer",
            "consumer_address": "Street 1",
            "consumer_tariff": tariff.id,
            "consumer_division": "division1",
        },
        format="json",
    )
    assert resp.status_code == 201
    consumer = Consumer.objects.get(consumer_number="C888001")
    assert consumer.approved is False
    assert consumer.user.is_consumer is True


def test_registration_rejects_duplicate_email(api_client, tariff):
    from tests.factories import UserFactory

    UserFactory(email="dupe@consumer.test")
    resp = api_client.post(
        "/api/v1/consumers/register/",
        {
            "email": "dupe@consumer.test",
            "password": "An0therStr0ng!",
            "consumer_number": "C777001",
            "consumer_name": "X",
            "consumer_address": "Y",
            "consumer_tariff": tariff.id,
            "consumer_division": "division1",
        },
        format="json",
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "validation_error"


def test_sdo_can_approve_pending_consumer(auth_for):
    consumer = UnapprovedConsumerFactory()
    sdo = SDOUserFactory()
    client = auth_for(sdo)

    resp = client.post(f"/api/v1/consumers/{consumer.id}/approve/")
    assert resp.status_code == 200
    consumer.refresh_from_db()
    assert consumer.approved is True


def test_double_approval_conflicts(auth_for):
    consumer = UnapprovedConsumerFactory()
    sdo = SDOUserFactory()
    client = auth_for(sdo)
    client.post(f"/api/v1/consumers/{consumer.id}/approve/")
    resp = client.post(f"/api/v1/consumers/{consumer.id}/approve/")
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "conflict"


def test_consumer_role_cannot_approve(auth_for):
    consumer = UnapprovedConsumerFactory()
    user = ConsumerUserFactory()
    client = auth_for(user)
    resp = client.post(f"/api/v1/consumers/{consumer.id}/approve/")
    assert resp.status_code == 403


def test_sdo_can_reject_unapproved_consumer(auth_for):
    consumer = UnapprovedConsumerFactory()
    sdo = SDOUserFactory()
    client = auth_for(sdo)

    resp = client.post(f"/api/v1/consumers/{consumer.id}/reject/")
    assert resp.status_code == 200
    assert not Consumer.objects.filter(id=consumer.id).exists()


def test_rejecting_approved_consumer_conflicts(auth_for):
    from tests.factories import ConsumerFactory

    consumer = ConsumerFactory(approved=True)
    sdo = SDOUserFactory()
    client = auth_for(sdo)
    resp = client.post(f"/api/v1/consumers/{consumer.id}/reject/")
    assert resp.status_code == 409


def test_consumer_self_profile(auth_for):
    consumer = UnapprovedConsumerFactory()
    client = auth_for(consumer.user)

    resp = client.get("/api/v1/consumers/me/")
    assert resp.status_code == 200
    assert resp.json()["data"]["consumer_number"] == consumer.consumer_number

    resp2 = client.patch(
        "/api/v1/consumers/me/", {"consumer_name": "Renamed"}, format="json"
    )
    assert resp2.status_code == 200
    consumer.refresh_from_db()
    assert consumer.consumer_name == "Renamed"
