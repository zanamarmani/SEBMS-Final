"""SEBMS URL configuration — headless JSON API only (/api/v1/...)."""
from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.db import connection
from core.worker_health import WorkerHealthView


def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok"})
    except Exception:
        return JsonResponse({"status": "unavailable"}, status=503)

urlpatterns = [
    path("health/", health),
    path("api/v1/system/worker-health/", WorkerHealthView.as_view()),
    path("admin/", admin.site.urls),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("SDO.urls")),
    path("api/v1/", include("consumer.urls")),
    path("api/v1/", include("meterreader.urls")),
    path("api/v1/", include("bill.urls")),
    path("api/v1/", include("payment.urls")),
    path("api/v1/", include("officestaff.urls")),
]
