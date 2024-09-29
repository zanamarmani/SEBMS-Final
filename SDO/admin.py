# consumer/admin.py

from django.contrib import admin
from .models import Tariff

@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('tariff_type', 'price_100', 'price_200', 'price_300', 'price_above')
    search_fields = ('tariff_type',)
    list_filter = ('tariff_type',)
