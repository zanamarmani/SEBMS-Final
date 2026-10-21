from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("bills", views.BillViewSet, basename="bill")

# Explicit paths first — router detail route would shadow "bills/generate/".
urlpatterns = [
    path("bills/generate/", views.GenerateBillsView.as_view(), name="bills-generate"),
    path("", include(router.urls)),
]
