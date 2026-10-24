"""Meter & meter-reading API views."""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.permissions import CanCaptureReadings, IsConsumer, IsOfficeStaff
from consumer.models import Consumer
from meterreader.models import Meter, MeterReading
from meterreader.serializers import MeterReadingSerializer, MeterSerializer
from core.services.firebase import fetch_meter_list
from core.services.meter_readings import ingest_meter_data


class MeterViewSet(viewsets.ModelViewSet):
    """Meter management.

    - Consumers see only their own meters.
    - Office staff / SDO manage assignments (create validates consumer approval).
    """

    serializer_class = MeterSerializer
    search_fields = ["meter_number"]
    filterset_fields = ["meter_type", "consumer"]
    ordering_fields = ["id", "meter_number"]

    def get_queryset(self):
        qs = Meter.objects.select_related(
            "consumer", "consumer__consumer_tariff"
        ).order_by("id")
        user = self.request.user
        if user.is_superuser or user.is_sdo or user.is_office_staff:
            return qs
        if user.is_meter_reader:
            # Readers must be able to pick the meter they are capturing for.
            return qs
        if user.is_consumer:
            return qs.filter(consumer__user=user)
        return qs.none()

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return [IsOfficeStaff()]


class MeterReadingViewSet(viewsets.ModelViewSet):
    """Meter-reading capture & listing.

    - Create: meter readers & office staff (auto-computes last_reading,
      validates image size/type).
    - List/retrieve: office staff, SDO, meter readers.
    """

    serializer_class = MeterReadingSerializer
    filterset_fields = ["meter", "processed", "reading_date"]
    ordering_fields = ["id", "reading_date"]

    def get_queryset(self):
        return MeterReading.objects.select_related(
            "meter", "meter__consumer"
        ).order_by("-reading_date", "-id")

    def get_permissions(self):
        return [CanCaptureReadings()]


class SyncMeterReadingsView(APIView):
    """Import Firestore readings immediately without requiring a queue worker."""

    permission_classes = [IsOfficeStaff]

    def post(self, request):
        records = fetch_meter_list(strict=True)
        stats = ingest_meter_data(records)
        return Response({"status": "COMPLETED", **stats})


class MyMetersView(APIView):
    """GET /api/v1/meters/me/ — the authenticated consumer's meters."""

    permission_classes = [IsConsumer]

    def get(self, request):
        consumer = get_object_or_404(Consumer, user=request.user)
        meters = Meter.objects.filter(consumer=consumer).select_related("consumer")
        return Response(MeterSerializer(meters, many=True).data)
