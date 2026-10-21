"""Celery application for SEBMS.

Loaded eagerly by SEBMS/__init__.py so `celery -A SEBMS worker` and
`celery -A SEBMS beat` pick up the configuration. Broker/backend URLs
come from Django settings (env-driven).
"""
import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SEBMS.settings")

app = Celery("SEBMS")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
