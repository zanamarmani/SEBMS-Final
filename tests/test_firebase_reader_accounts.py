from unittest.mock import patch

import pytest

from core.services.firebase_users import ScannerUnavailable
from tests.factories import SDOUserFactory, ConsumerUserFactory, PASSWORD
from users.models import User
from users.serializers import UserAdminSerializer

pytestmark = pytest.mark.django_db


def reader(email='scanner@example.com'):
    return {'email': email, 'password': PASSWORD, 'role': 'meter_reader'}


def test_sdo_creates_reader_in_both_systems(api_client):
    api_client.force_authenticate(SDOUserFactory())
    with patch('core.services.firebase_users.create_reader', return_value='reader-uid') as create:
        response = api_client.post('/api/v1/users/', reader(), format='json')
    assert response.status_code == 201
    user = User.objects.get(email='scanner@example.com')
    assert user.is_meter_reader and user.firebase_uid == 'reader-uid'
    assert user.check_password(PASSWORD)
    create.assert_called_once_with(user.email, PASSWORD, True)
    assert 'password' not in response.json()['data']


def test_firebase_failure_rolls_back_django_user(api_client):
    api_client.force_authenticate(SDOUserFactory())
    with patch('core.services.firebase_users.create_reader', side_effect=ScannerUnavailable()):
        response = api_client.post('/api/v1/users/', reader(), format='json')
    assert response.status_code == 503
    assert not User.objects.filter(email='scanner@example.com').exists()


def test_non_sdo_cannot_provision(api_client):
    api_client.force_authenticate(ConsumerUserFactory())
    with patch('core.services.firebase_users.create_reader') as create:
        response = api_client.post('/api/v1/users/', reader(), format='json')
    assert response.status_code == 403
    create.assert_not_called()


def test_other_roles_do_not_need_firebase():
    data = {**reader(), 'role': 'office_staff'}
    with patch('core.services.firebase_users.create_reader') as create:
        serializer = UserAdminSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        user = serializer.save()
    assert user.is_office_staff and user.firebase_uid is None
    create.assert_not_called()


def test_existing_reader_can_be_provisioned_by_password_reset():
    user = User.objects.create_user(email='old@example.com', password=PASSWORD, is_meter_reader=True)
    serializer = UserAdminSerializer(user, data={'password': PASSWORD}, partial=True)
    assert serializer.is_valid(), serializer.errors
    with patch('core.services.firebase_users.create_reader', return_value='new-uid'):
        updated = serializer.save()
    assert updated.firebase_uid == 'new-uid'


def test_disable_reader_synchronizes_firebase():
    user = User.objects.create_user(email='old@example.com', password=PASSWORD, is_meter_reader=True, firebase_uid='uid')
    serializer = UserAdminSerializer(user, data={'is_active': False}, partial=True)
    assert serializer.is_valid(), serializer.errors
    with patch('core.services.firebase_users.sync_reader') as sync:
        updated = serializer.save()
    assert not updated.is_active
    sync.assert_called_once_with(updated, None)


def test_update_failure_does_not_change_local_password():
    user = User.objects.create_user(email='old@example.com', password=PASSWORD, is_meter_reader=True, firebase_uid='uid')
    serializer = UserAdminSerializer(user, data={'password': 'AnotherValidPass!33'}, partial=True)
    assert serializer.is_valid(), serializer.errors
    with patch('core.services.firebase_users.sync_reader', side_effect=ScannerUnavailable()):
        with pytest.raises(ScannerUnavailable):
            serializer.save()
    user.refresh_from_db()
    assert user.check_password(PASSWORD)


def test_firebase_service_sets_only_reader_claim():
    from core.services import firebase_users
    with patch.object(firebase_users, 'get_auth_app', return_value='app'), \
         patch.object(firebase_users.auth, 'create_user') as create, \
         patch.object(firebase_users.auth, 'set_custom_user_claims') as claims:
        uid = firebase_users.create_reader('reader@example.com', PASSWORD, True)
    assert uid.startswith('sebms_')
    create.assert_called_once_with(uid=uid, email='reader@example.com', password=PASSWORD, disabled=False, app='app')
    claims.assert_called_once_with(uid, {'meter_reader': True}, app='app')


def test_claim_failure_removes_new_firebase_identity():
    from core.services import firebase_users
    with patch.object(firebase_users, 'get_auth_app', return_value='app'), \
         patch.object(firebase_users.auth, 'create_user'), \
         patch.object(firebase_users.auth, 'set_custom_user_claims', side_effect=RuntimeError('provider error')), \
         patch.object(firebase_users.auth, 'delete_user') as delete:
        with pytest.raises(ScannerUnavailable):
            firebase_users.create_reader('reader@example.com', PASSWORD, True)
    delete.assert_called_once()


def test_disabled_reader_revokes_refresh_tokens():
    from core.services import firebase_users
    from types import SimpleNamespace
    user = SimpleNamespace(firebase_uid='uid', email='reader@example.com', is_active=False, is_meter_reader=True)
    with patch.object(firebase_users, 'get_auth_app', return_value='app'), \
         patch.object(firebase_users.auth, 'update_user') as update, \
         patch.object(firebase_users.auth, 'revoke_refresh_tokens') as revoke:
        firebase_users.sync_reader(user)
    update.assert_called_once_with('uid', app='app', email=user.email, disabled=True)
    revoke.assert_called_once_with('uid', app='app')
