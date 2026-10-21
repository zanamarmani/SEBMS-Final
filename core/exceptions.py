"""DRF exception handler producing a consistent API error envelope.

Response contract (see ./prompts/modules/api.md):
    {"success": false, "data": null, "error": {"code": "...", "message": "...", "details": ...}}
Unhandled server errors never leak stack traces or internal identifiers.
"""
from __future__ import annotations

import logging

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "conflict"
    default_detail = "The request conflicts with the current state of the resource."


_CODE_BY_STATUS = {
    status.HTTP_400_BAD_REQUEST: "validation_error",
    status.HTTP_401_UNAUTHORIZED: "unauthenticated",
    status.HTTP_403_FORBIDDEN: "permission_denied",
    status.HTTP_404_NOT_FOUND: "not_found",
    status.HTTP_405_METHOD_NOT_ALLOWED: "method_not_allowed",
    status.HTTP_409_CONFLICT: "conflict",
    429: "throttled",
}


def _envelope(code: str, message: str, details=None) -> dict:
    return {
        "success": False,
        "data": None,
        "error": {"code": code, "message": message, "details": details},
    }


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        # Unhandled exception (Http404/PermissionDenied/DjangoValidationError
        # are already converted by DRF; anything reaching here is a 500).
        if isinstance(exc, (Http404, DjangoPermissionDenied, APIException)):
            raise exc
        logger.exception("Unhandled API exception", exc_info=exc)
        return Response(
            _envelope("server_error", "An unexpected error occurred."),
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    code = _CODE_BY_STATUS.get(response.status_code, f"http_{response.status_code}")
    default_message = getattr(exc, "detail", None)
    if isinstance(default_message, dict) or isinstance(default_message, list):
        message = "Request validation failed."
        details = default_message
    else:
        message = str(default_message) if default_message else "Request failed."
        details = None

    response.data = _envelope(code, message, details)
    return response
