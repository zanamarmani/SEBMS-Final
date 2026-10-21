"""Pagination classes for the SEBMS API."""
from rest_framework.pagination import CursorPagination, PageNumberPagination


class DefaultPagination(PageNumberPagination):
    """Offset pagination for small, stable collections."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class CursorPaginationBill(CursorPagination):
    """Cursor pagination for large, frequently updated collections
    (bills, meter readings)."""

    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
    ordering = "-id"
