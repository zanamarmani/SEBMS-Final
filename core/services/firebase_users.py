"""Server-side scanner identity provisioning. Never log user passwords."""
import json
import logging
import uuid

import firebase_admin
from firebase_admin import auth, credentials
from django.conf import settings
from rest_framework.exceptions import APIException

from core.exceptions import Conflict

logger = logging.getLogger(__name__)
APP_NAME = 'sebms-scanner-auth'


class ScannerUnavailable(APIException):
    status_code = 503
    default_code = 'scanner_unavailable'
    default_detail = 'Scanner account could not be synchronized. Contact the administrator and retry.'


def get_auth_app():
    try:
        return firebase_admin.get_app(APP_NAME)
    except ValueError:
        pass
    try:
        raw = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_JSON', '')
        source = json.loads(raw) if raw else settings.FIREBASE_CREDENTIALS_PATH
        cert = credentials.Certificate(source)
        expected = getattr(settings, 'FIREBASE_PROJECT_ID', 'sebms-81d12')
        if cert.project_id != expected:
            raise ValueError('Firebase project mismatch')
        return firebase_admin.initialize_app(cert, {'projectId': expected, 'httpTimeout': 15}, name=APP_NAME)
    except Exception:
        # SDK errors may include credential material; return a fixed message.
        logger.error('Scanner Firebase Admin configuration is unavailable')
        raise ScannerUnavailable() from None


def create_reader(email, password, active):
    app = get_auth_app()
    uid = 'sebms_' + uuid.uuid4().hex
    try:
        auth.create_user(uid=uid, email=email, password=password, disabled=not active, app=app)
    except auth.EmailAlreadyExistsError:
        raise Conflict('This email already has a Firebase account. Contact the administrator to link it safely.') from None
    except Exception:
        remove_new_reader(uid)
        raise ScannerUnavailable() from None
    try:
        auth.set_custom_user_claims(uid, {'meter_reader': True}, app=app)
    except Exception:
        remove_new_reader(uid)
        raise ScannerUnavailable() from None
    return uid


def remove_new_reader(uid):
    """Compensate a new account if the Django transaction failed."""
    try:
        auth.delete_user(uid, app=get_auth_app())
    except Exception:
        logger.error('Scanner account cleanup needs administrator reconciliation; uid=%s', uid)


def sync_reader(user, password=None):
    if not user.firebase_uid:
        raise ScannerUnavailable('This existing reader needs a password reset to enable scanner login.')
    app = get_auth_app()
    changes = {'email': user.email, 'disabled': not (user.is_active and user.is_meter_reader)}
    if password is not None:
        changes['password'] = password
    try:
        if changes['disabled'] or password is not None:
            auth.revoke_refresh_tokens(user.firebase_uid, app=app)
        auth.update_user(user.firebase_uid, app=app, **changes)
    except auth.EmailAlreadyExistsError:
        raise Conflict('This email already belongs to another Firebase account.') from None
    except Exception:
        raise ScannerUnavailable() from None
