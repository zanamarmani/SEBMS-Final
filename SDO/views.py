"""SDO API views — tariffs, dashboard stats, consumer approvals, profile."""
from django.db.models import Count, Q, Sum
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from bill.models import Bill
from core.exceptions import Conflict
from core.permissions import IsSDO
from consumer.models import Consumer
from payment.models import Payment
from users.models import User

from .models import Tariff, sdo_profile
from .serializers import SDOProfileSerializer, TariffSerializer


class TariffViewSet(viewsets.ModelViewSet):
    """Tariff management: SDO writes, public reads (registration needs pricing)."""

    serializer_class = TariffSerializer
    queryset = Tariff.objects.all().order_by("id")
    search_fields = ["tariff_type"]
    ordering_fields = ["id", "tariff_type"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsSDO()]


class ApproveConsumerView(APIView):
    """POST /api/v1/consumers/<pk>/approve/"""

    permission_classes = [IsSDO]

    def post(self, request, pk: int):
        try:
            consumer = Consumer.objects.select_related("consumer_tariff").get(pk=pk)
        except Consumer.DoesNotExist:
            raise Http404("Consumer not found.")
        if consumer.approved:
            raise Conflict("Consumer is already approved.")
        consumer.approved = True
        consumer.save(update_fields=["approved"])
        return Response({"id": consumer.id, "approved": True})


class RejectConsumerView(APIView):
    """POST /api/v1/consumers/<pk>/reject/ — deletes an unapproved consumer."""

    permission_classes = [IsSDO]

    def post(self, request, pk: int):
        try:
            consumer = Consumer.objects.get(pk=pk)
        except Consumer.DoesNotExist:
            raise Http404("Consumer not found.")
        if consumer.approved:
            raise Conflict("Approved consumers cannot be rejected; delete them instead.")
        consumer_id = consumer.id
        consumer.delete()
        return Response({"id": consumer_id, "deleted": True}, status=status.HTTP_200_OK)


class DashboardStatsView(APIView):
    """GET /api/v1/dashboard/stats/ — SDO dashboard aggregates (3 queries)."""

    permission_classes = [IsSDO]

    def get(self, request):
        user_stats = User.objects.aggregate(
            total=Count("id"),
            sdo=Count("id", filter=Q(is_sdo=True)),
            office_staff=Count("id", filter=Q(is_office_staff=True)),
            meter_reader=Count("id", filter=Q(is_meter_reader=True)),
            consumer=Count("id", filter=Q(is_consumer=True)),
        )
        consumer_stats = Consumer.objects.aggregate(
            total=Count("id"),
            approved_count=Count("id", filter=Q(approved=True)),
            pending_count=Count("id", filter=Q(approved=False)),
        )
        bill_stats = Bill.objects.aggregate(
            total=Count("id"),
            paid_count=Count("id", filter=Q(paid=True)),
            unpaid_count=Count("id", filter=Q(paid=False)),
            total_collected=Sum("payableamount", filter=Q(paid=True)),
        )
        payment_stats = Payment.objects.filter(status=Payment.Status.SUCCESS).aggregate(
            total_success=Count("id"),
            total_amount=Sum("amount"),
        )
        return Response(
            {
                "users": user_stats,
                "consumers": consumer_stats,
                "bills": bill_stats,
                "payments": payment_stats,
            }
        )


class SDOProfileView(APIView):
    """GET/PATCH /api/v1/sdo/profile/ — the authenticated SDO's own profile."""

    permission_classes = [IsSDO]

    def _get_profile(self) -> sdo_profile:
        profile = sdo_profile.objects.filter(user=self.request.user).first()
        if profile is None:
            raise Http404("SDO profile not found.")
        return profile

    def get(self, request):
        return Response(SDOProfileSerializer(self._get_profile()).data)

    def post(self, request):
        if sdo_profile.objects.filter(user=request.user).exists():
            raise Conflict("Profile already exists; use PATCH to update.")
        serializer = SDOProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        serializer = SDOProfileSerializer(
            self._get_profile(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
