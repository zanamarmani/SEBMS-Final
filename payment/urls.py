from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("payments", views.PaymentViewSet, basename="payment")

# Explicit action paths must precede the router: the router's detail route
# (payments/<pk>/) would otherwise swallow "payments/callback/".
urlpatterns = [
    path(
        "payments/initiate/<int:bill_id>/",
        views.InitiatePaymentView.as_view(),
        name="payment-initiate",
    ),
    path(
        "payments/callback/",
        views.PaymentCallbackView.as_view(),
        name="payment-callback",
    ),
    path("", include(router.urls)),
]
