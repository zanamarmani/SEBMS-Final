from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("consumers", views.ConsumerViewSet, basename="consumer")

urlpatterns = [
    path("consumers/register/", views.RegisterConsumerView.as_view(), name="consumer-register"),
    path("", include(router.urls)),
]
