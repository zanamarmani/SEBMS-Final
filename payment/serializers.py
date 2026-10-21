"""Payment serializers."""
from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    bill_paid = serializers.BooleanField(source="bill.paid", read_only=True, default=None)
    bill_amount = serializers.DecimalField(
        source="bill.payableamount", max_digits=10, decimal_places=2, read_only=True, default=None
    )

    class Meta:
        model = Payment
        fields = [
            "id",
            "bill",
            "bill_paid",
            "bill_amount",
            "reference",
            "amount",
            "bank_charges",
            "arrears_charges",
            "status",
            "created_at",
        ]
        read_only_fields = fields
