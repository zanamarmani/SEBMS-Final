from unittest.mock import patch

import pytest

from tests.factories import SDOUserFactory, ConsumerUserFactory, MeterReaderUserFactory, OfficeStaffUserFactory

pytestmark = pytest.mark.django_db
URL = '/api/v1/system/worker-health/'


def test_sdo_probes_real_broker_without_retries(api_client):
    api_client.force_authenticate(SDOUserFactory())
    with patch('core.worker_health.app') as app:
        app.control.ping.return_value = [{'worker': {'ok': 'pong'}}]
        response = api_client.get(URL)
    assert response.status_code == 200
    assert response.json()['data'] == {'status': 'ok', 'workers': 1}
    connection = app.connection_for_write.return_value.__enter__.return_value
    connection.ensure_connection.assert_called_once_with(max_retries=0)
    app.control.ping.assert_called_once_with(timeout=3, connection=connection)


def test_missing_worker_returns_unavailable(api_client):
    api_client.force_authenticate(SDOUserFactory())
    with patch('core.worker_health.app') as app:
        app.control.ping.return_value = []
        response = api_client.get(URL)
    assert response.status_code == 503
    assert response.json()['data']['status'] == 'worker_unavailable'


def test_broker_error_does_not_expose_credentials(api_client):
    api_client.force_authenticate(SDOUserFactory())
    with patch('core.worker_health.app') as app:
        app.connection_for_write.side_effect = RuntimeError('rediss://:private-password@example.com')
        response = api_client.get(URL)
    assert response.status_code == 503
    assert response.json()['data']['status'] == 'broker_unavailable'
    assert b'private-password' not in response.content


@pytest.mark.parametrize('factory', [ConsumerUserFactory, MeterReaderUserFactory, OfficeStaffUserFactory])
def test_non_sdo_cannot_contact_broker(api_client, factory):
    api_client.force_authenticate(factory())
    with patch('core.worker_health.app') as app:
        response = api_client.get(URL)
    assert response.status_code == 403
    app.connection_for_write.assert_not_called()


def test_anonymous_cannot_contact_broker(api_client):
    with patch('core.worker_health.app') as app:
        response = api_client.get(URL)
    assert response.status_code == 401
    app.connection_for_write.assert_not_called()
