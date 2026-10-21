"""Consumer API views — public registration, staff management, self profile."""
from django.db.models import Prefetch
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from core.permissions import IsConsumer, IsOfficeStaff
from consumer.models import Consumer
from consumer.serializers import (
    ConsumerRegistrationSerializer,
    ConsumerSelfUpdateSerializer,
    ConsumerSerializer,
)
from meterreader.models import Meter


class RegisterConsumerView(APIView):
    """POST /api/v1/consumers/register/ — public self-registration."""

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"

    def post(self, request):
        serializer = ConsumerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        consumer = serializer.save()
        return Response(
            ConsumerSerializer(consumer).data,
            status=status.HTTP_201_CREATED,
        )


class ConsumerViewSet(viewsets.ModelViewSet):
    """Consumer management.

    - list/retrieve/update/destroy: office staff, SDO, superuser
    - me: the authenticated consumer's own profile
    """

    serializer_class = ConsumerSerializer
    search_fields = ["consumer_number", "consumer_name", "consumer_address"]
    filterset_fields = ["approved", "consumer_division", "consumer_tariff"]
    ordering_fields = ["id", "consumer_number", "consumer_name"]

    def get_permissions(self):
        if self.action == "me":
            return [IsConsumer()]
        if self.action in ("list", "retrieve"):
            return [IsOfficeStaff()]
        return [IsOfficeStaff()]

    def get_queryset(self):
        qs = (
            Consumer.objects.select_related("consumer_tariff", "user")
            .prefetch_related(Prefetch("meters", queryset=Meter.objects.only("meter_number")))
            .order_by("id")
        )
        user = self.request.user
        if user.is_superuser or user.is_sdo or user.is_office_staff:
            return qs
        return qs.filter(user=user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        if not (request.user.is_superuser or request.user.is_sdo or request.user.is_office_staff):
            serializer = ConsumerSelfUpdateSerializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(ConsumerSerializer(instance).data)
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=["get", "patch"], permission_classes=[IsConsumer])
    def me(self, request):
        consumer = Consumer.objects.select_related("consumer_tariff", "user").filter(
            user=request.user
        ).first()
        if consumer is None:
            raise Http404("Consumer profile not found.")
        if request.method == "PATCH":
            serializer = ConsumerSelfUpdateSerializer(consumer, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(ConsumerSerializer(consumer).data)
