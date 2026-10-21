"""Payment API views — initiate (mock) & callback settlement."""
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bill.models import Bill
from core.services.payments import initiate_payment, process_payment_callback
from payment.models import Payment
from payment.serializers import PaymentSerializer
from payment.tasks import send_payment_receipt_email


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    """Payment history.

    - Office staff / SDO: all payments.
    - Consumers: payments against their own bills only.
    """

    serializer_class = PaymentSerializer
    filterset_fields = ["status", "bill"]
    ordering_fields = ["id", "created_at"]

    def get_queryset(self):
        qs = Payment.objects.select_related(
            "bill", "bill__meter", "bill__meter__consumer"
        ).order_by("-created_at", "-id")
        user = self.request.user
        if user.is_superuser or user.is_sdo or user.is_office_staff:
            return qs
        if user.is_consumer:
            return qs.filter(bill__meter__consumer__user=user)
        return qs.none()

    def get_permissions(self):
        return [IsAuthenticated()]


class InitiatePaymentView(APIView):
    """POST /api/v1/payments/initiate/<bill_id>/ — build gateway payload.

    Consumers may only initiate payments for their own unpaid bills.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, bill_id: int):
        qs = Bill.objects.select_related("meter", "meter__consumer")
        user = request.user
        if not (user.is_superuser or user.is_sdo or user.is_office_staff):
            qs = qs.filter(meter__consumer__user=user)
        bill = qs.filter(id=bill_id).first()
        if bill is None:
            raise Http404("Bill not found.")
        try:
            payload = initiate_payment(bill)
        except ValueError as exc:
            return Response(
                {"success": False, "data": None,
                 "error": {"code": "conflict", "message": str(exc), "details": None}},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(payload)


class PaymentCallbackView(APIView):
    """POST /api/v1/payments/callback/ — gateway (or mock client) settlement.

    Public endpoint: identity comes from the signed payload, not a token.
    Verifies the secure hash + amount, then settles idempotently.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        txn_ref_no = request.data.get("pp_TxnRefNo")
        amount = request.data.get("pp_Amount")
        response_code = str(request.data.get("pp_ResponseCode", ""))
        secure_hash = str(request.data.get("pp_SecureHash", ""))

        missing = [
            name for name, val in [
                ("pp_TxnRefNo", txn_ref_no), ("pp_Amount", amount),
                ("pp_ResponseCode", response_code), ("pp_SecureHash", secure_hash),
            ] if val in (None, "")
        ]
        if missing:
            return Response(
                {"success": False, "data": None,
                 "error": {"code": "validation_error", "message": "Missing fields.",
                           "details": {"missing": missing}}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = process_payment_callback(
                txn_ref_no=txn_ref_no,
                amount_paisa=int(amount),
                response_code=response_code,
                secure_hash=secure_hash,
            )
        except ValueError as exc:
            return Response(
                {"success": False, "data": None,
                 "error": {"code": "validation_error", "message": str(exc), "details": None}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if result["status"] == "success" and "Duplicate" not in result["detail"]:
            send_payment_receipt_email.delay(result["bill_id"], result["payment_id"])
        return Response(result)
