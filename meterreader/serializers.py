"""Meter & meter-reading serializers."""
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from consumer.models import Consumer
from core.services.meter_readings import INITIAL_LAST_READING
from meterreader.models import Meter, MeterReading

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


class MeterConsumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consumer
        fields = ["id", "consumer_number", "consumer_name", "approved"]


class MeterSerializer(serializers.ModelSerializer):
    consumer_detail = MeterConsumerSerializer(source="consumer", read_only=True)

    class Meta:
        model = Meter
        fields = ["id", "meter_number", "meter_type", "consumer", "consumer_detail"]

    def validate_meter_number(self, value):
        qs = Meter.objects.filter(meter_number=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A meter with this number already exists.")
        return value

    def validate_consumer(self, consumer):
        if consumer is not None and not consumer.approved:
            raise serializers.ValidationError(
                "Meters can only be assigned to approved consumers."
            )
        return consumer


class MeterReadingSerializer(serializers.ModelSerializer):
    meter_number = serializers.IntegerField(source="meter.meter_number", read_only=True)

    class Meta:
        model = MeterReading
        fields = [
            "id",
            "meter",
            "meter_number",
            "last_reading",
            "new_reading",
            "meter_status",
            "processed",
            "reading_date",
            "meter_image",
        ]
        read_only_fields = ["id", "last_reading", "processed"]

    def validate_meter_image(self, image):
        if image is None:
            return image
        if image.size > MAX_IMAGE_SIZE:
            raise serializers.ValidationError("Image must be 5 MB or smaller.")
        try:
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])(image)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(
                "Only JPG, PNG, or WEBP images are allowed."
            ) from exc
        return image

    def create(self, validated_data: dict) -> MeterReading:
        """Auto-fill last_reading from the meter's most recent reading."""
        meter = validated_data["meter"]
        last = (
            MeterReading.objects.filter(meter=meter)
            .order_by("-reading_date", "-id")
            .values_list("new_reading", flat=True)
            .first()
        )
        validated_data["last_reading"] = last if last is not None else INITIAL_LAST_READING

        new_reading = validated_data.get("new_reading")
        if new_reading is not None and validated_data["last_reading"] is not None:
            if new_reading < validated_data["last_reading"]:
                raise serializers.ValidationError(
                    {"new_reading": "New reading cannot be less than the last reading."}
                )
        return super().create(validated_data)
