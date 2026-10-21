"""Role-based permissions.

Roles are resolved exclusively from the authenticated server-side user
record — client-supplied roles, user ids, or tenant claims are never trusted
(see ./prompts/modules/security.md).
"""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSDO(BasePermission):
    message = "SDO role required."

    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and (user.is_sdo or user.is_superuser))


class IsOfficeStaff(BasePermission):
    message = "Office staff role required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_office_staff or user.is_sdo or user.is_superuser)
        )


class IsMeterReader(BasePermission):
    message = "Meter reader role required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (user.is_meter_reader or user.is_superuser)
        )


class CanCaptureReadings(BasePermission):
    """Meter readers capture readings; office staff/SDO manage them too."""

    message = "Meter reader or office staff role required."

    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        return bool(
            (user.is_meter_reader or user.is_superuser)
            or (user.is_office_staff or user.is_sdo)
        )


class IsConsumer(BasePermission):
    message = "Consumer role required."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and (user.is_consumer or user.is_superuser)
        )


class IsOwnerOrStaff(BasePermission):
    """Object-level: allow the owning consumer, or any office/SDO/superuser."""

    message = "You may only access your own records."

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser or user.is_sdo or user.is_office_staff:
            return True
        owner = getattr(obj, "consumer", None) or (
            obj if user.is_consumer else None
        )
        if owner is not None:
            if hasattr(owner, "user_id") and owner.user_id == user.id:
                return True
        return False


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
