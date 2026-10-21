"""SDO app serializers."""
from rest_framework import serializers

from SDO.models import Tariff, sdo_profile


class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = ["id", "tariff_type", "price_100", "price_200", "price_300", "price_above"]

    def validate_tariff_type(self, value):
        qs = Tariff.objects.filter(tariff_type=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A tariff of this type already exists.")
        return value

    def _validate_non_negative(self, attrs):
        for field in ("price_100", "price_200", "price_300", "price_above"):
            value = attrs.get(field, getattr(self.instance, field, None))
            if value is not None and value < 0:
                raise serializers.ValidationError({field: "Price cannot be negative."})

    def validate(self, attrs):
        self._validate_non_negative(attrs)
        return attrs


class SDOProfileSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = sdo_profile
        fields = ["id", "user_email", "first_name", "last_name", "office_location", "joining_date"]
