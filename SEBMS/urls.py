"""SEBMS URL configuration — headless JSON API only (/api/v1/...)."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("users.urls")),
    path("api/v1/", include("SDO.urls")),
    path("api/v1/", include("consumer.urls")),
    path("api/v1/", include("meterreader.urls")),
    path("api/v1/", include("bill.urls")),
    path("api/v1/", include("payment.urls")),
    path("api/v1/", include("officestaff.urls")),
]
