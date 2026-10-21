"""User & auth serializers."""
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users.models import User

ROLE_FIELD_MAP = {
    "sdo": "is_sdo",
    "office_staff": "is_office_staff",
    "meter_reader": "is_meter_reader",
    "consumer": "is_consumer",
}
ROLE_CHOICES = tuple(ROLE_FIELD_MAP.keys())


class UserSerializer(serializers.ModelSerializer):
    """Read-only projection of a user with a single logical role."""

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "email", "role", "is_active", "is_superuser"]
        read_only_fields = ["id", "email", "is_superuser"]

    def get_role(self, obj) -> str | None:
        for role, field in ROLE_FIELD_MAP.items():
            if getattr(obj, field, False):
                return role
        return None


class UserAdminSerializer(serializers.ModelSerializer):
    """SDO-facing serializer: create/update users with a single role."""

    role = serializers.ChoiceField(choices=ROLE_CHOICES)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ["id", "email", "role", "password", "is_active"]

    def _apply_role(self, user: User, role: str) -> None:
        for r, field in ROLE_FIELD_MAP.items():
            setattr(user, field, r == role)

    def to_representation(self, instance) -> dict:
        return UserSerializer(instance).data

    def validate_email(self, value: str) -> str:
        qs = User.objects.filter(email__iexact=value)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data: dict) -> User:
        role = validated_data.pop("role")
        password = validated_data.pop("password")
        user = User.objects.create_user(
            email=validated_data.pop("email"), password=password, **validated_data
        )
        self._apply_role(user, role)
        user.save()
        return user

    def update(self, instance: User, validated_data: dict) -> User:
        role = validated_data.pop("role", None)
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if role is not None:
            self._apply_role(instance, role)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
