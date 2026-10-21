from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("meters", views.MeterViewSet, basename="meter")
router.register("meter-readings", views.MeterReadingViewSet, basename="meter-reading")

# Explicit paths first — router detail routes would shadow these actions.
urlpatterns = [
    path(
        "meter-readings/sync/",
        views.SyncMeterReadingsView.as_view(),
        name="meter-readings-sync",
    ),
    path("meters/me/", views.MyMetersView.as_view(), name="my-meters"),
    path("", include(router.urls)),
]
