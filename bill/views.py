"""Bill API views."""
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bill.models import Bill
from bill.serializers import BillSerializer
from core.services.meter_readings import generate_bills_for_unprocessed_readings
from core.pagination import CursorPaginationBill
from core.permissions import IsOfficeStaff


class BillViewSet(viewsets.ReadOnlyModelViewSet):
    """Bill listing with cursor pagination.

    - Office staff / SDO: all bills, filterable by paid/meter.
    - Consumers: only bills belonging to their own meters.
    """

    serializer_class = BillSerializer
    pagination_class = CursorPaginationBill
    filterset_fields = ["paid", "meter", "billmonth"]
    ordering_fields = ["id", "billmonth", "payableamount"]

    def get_queryset(self):
        qs = Bill.objects.select_related(
            "meter", "meter__consumer"
        ).order_by("-id")
        user = self.request.user
        if user.is_superuser or user.is_sdo or user.is_office_staff:
            return qs
        if user.is_consumer:
            return qs.filter(meter__consumer__user=user)
        return qs.none()

    def get_permissions(self):
        return [IsAuthenticated()]


class GenerateBillsView(APIView):
    """POST /api/v1/bills/generate/ — complete bill generation immediately."""

    permission_classes = [IsOfficeStaff]

    def post(self, request):
        stats = generate_bills_for_unprocessed_readings()
        return Response({"status": "COMPLETED", **stats})
