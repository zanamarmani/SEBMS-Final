from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("tariffs", views.TariffViewSet, basename="tariff")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "consumers/<int:pk>/approve/",
        views.ApproveConsumerView.as_view(),
        name="consumer-approve",
    ),
    path(
        "consumers/<int:pk>/reject/",
        views.RejectConsumerView.as_view(),
        name="consumer-reject",
    ),
    path("dashboard/stats/", views.DashboardStatsView.as_view(), name="dashboard-stats"),
    path("sdo/profile/", views.SDOProfileView.as_view(), name="sdo-profile"),
]
