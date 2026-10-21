"""Auth (JWT) and user-management API views."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

from core.permissions import IsSDO
from users.models import User
from users.serializers import UserAdminSerializer, UserSerializer


class MeView(APIView):
    """GET /api/v1/auth/me/ — current identity + role (used by the SPA guard)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LoginView(TokenObtainPairView):
    """POST /api/v1/auth/login/ — issues access + refresh token pair."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class RefreshView(TokenRefreshView):
    """POST /api/v1/auth/refresh/ — rotates refresh, returns new pair."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class LogoutView(TokenBlacklistView):
    """POST /api/v1/auth/logout/ — blacklists the supplied refresh token."""

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "auth"


class UserViewSet(viewsets.ModelViewSet):
    """SDO-only user management."""

    permission_classes = [IsSDO]
    queryset = User.objects.all().order_by("id")
    search_fields = ["email"]
    ordering_fields = ["id", "email"]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return UserAdminSerializer
        return UserSerializer
