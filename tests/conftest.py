"""Pytest configuration — Celery runs eagerly in tests (no broker needed)."""
import os

os.environ.setdefault("CELERY_TASK_ALWAYS_EAGER", "true")
os.environ.setdefault("CELERY_TASK_EAGER_PROPAGATES", "true")

import pytest  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _eager_celery():
    """Force eager task execution for the whole test session.

    Settings may be imported before this conftest runs, so the env var alone
    cannot be trusted; write the final value after Django is configured and
    mirror it onto the Celery app.
    """
    from django.conf import settings

    settings.CELERY_TASK_ALWAYS_EAGER = True
    settings.CELERY_TASK_EAGER_PROPAGATES = True

    from SEBMS.celery import app as celery_app

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield


@pytest.fixture(autouse=True)
def _no_throttling(settings):
    """Disable API throttling inside the test suite (locmem cache is shared)."""
    settings.REST_FRAMEWORK = {
        **settings.REST_FRAMEWORK,
        "DEFAULT_THROTTLE_RATES": {
            "anon": "100000/day",
            "user": "100000/day",
            "auth": "100000/day",
        },
    }


@pytest.fixture(autouse=True)
def _fast_password_hashing(settings):
    """MD5 hasher for speed in tests only (production keeps strong hashers)."""
    settings.PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def auth_for():
    """Return a callable that authenticates an APIClient for a given user."""
    from rest_framework.test import APIClient

    def _auth(user, password="Str0ngPass!x"):
        client = APIClient()
        resp = client.post(
            "/api/v1/auth/login/",
            {"email": user.email, "password": password},
            format="json",
        )
        assert resp.status_code == 200, resp.content
        body = resp.json()
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {body['data']['access']}")
        client.refresh_token = body["data"]["refresh"]
        return client

    return _auth
