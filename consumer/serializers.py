"""Consumer serializers — registration, self-service, and staff views."""
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from SDO.models import Tariff
from SDO.serializers import TariffSerializer
from consumer.models import Consumer
from users.models import User


class ConsumerRegistrationSerializer(serializers.Serializer):
    """Public self-registration. Creates User + unapproved Consumer atomically."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    consumer_number = serializers.CharField(max_length=255)
    consumer_name = serializers.CharField(max_length=255)
    consumer_address = serializers.CharField(max_length=255)
    consumer_tariff = serializers.PrimaryKeyRelatedField(queryset=Tariff.objects.all())
    consumer_division = serializers.ChoiceField(choices=Consumer.DIVISION_CHOICES)

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_consumer_number(self, value: str) -> str:
        if Consumer.objects.filter(consumer_number=value).exists():
            raise serializers.ValidationError("This consumer number is already registered.")
        return value

    @transaction.atomic
    def create(self, validated_data: dict) -> Consumer:
        email = validated_data.pop("email")
        password = validated_data.pop("password")
        user = User.objects.create_user(email=email, password=password)
        user.is_consumer = True
        user.save(update_fields=["is_consumer"])
        return Consumer.objects.create(user=user, approved=False, **validated_data)


class ConsumerSerializer(serializers.ModelSerializer):
    consumer_tariff_detail = TariffSerializer(source="consumer_tariff", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    meter_numbers = serializers.SerializerMethodField()

    class Meta:
        model = Consumer
        fields = [
            "id",
            "user_email",
            "consumer_number",
            "consumer_name",
            "consumer_address",
            "consumer_tariff",
            "consumer_tariff_detail",
            "consumer_division",
            "approved",
            "meter_numbers",
        ]
        read_only_fields = ["id", "consumer_number", "approved", "user_email"]

    def get_meter_numbers(self, obj) -> list:
        meters = getattr(obj, "meters", None)
        if meters is None:
            return []
        return [m.meter_number for m in meters.all()]


class ConsumerSelfUpdateSerializer(serializers.ModelSerializer):
    """Consumers may edit only their own contact details."""

    class Meta:
        model = Consumer
        fields = ["id", "consumer_name", "consumer_address"]
