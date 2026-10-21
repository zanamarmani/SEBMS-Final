"""Bill serializers."""
from rest_framework import serializers

from bill.models import Bill


class BillSerializer(serializers.ModelSerializer):
    """Read-only bill projection with nested meter/consumer summary.

    Uses only in-memory attributes fetched via select_related in the view —
    no extra queries per row.
    """

    meter_info = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = [
            "id",
            "billmonth",
            "duedate",
            "detectionunit",
            "averageunit",
            "units",
            "unitsconsumed",
            "payableamount",
            "payable_after_due_date",
            "paid",
            "meter",
            "meter_info",
        ]
        read_only_fields = fields

    def get_meter_info(self, obj) -> dict | None:
        meter = obj.meter
        if meter is None:
            return None
        consumer = meter.consumer
        return {
            "id": meter.id,
            "meter_number": meter.meter_number,
            "consumer_number": getattr(consumer, "consumer_number", None),
            "consumer_name": getattr(consumer, "consumer_name", None),
        }
