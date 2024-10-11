from django.contrib import admin
from .models import Meter

@admin.register(Meter)
class MeterAdmin(admin.ModelAdmin):
    list_display = ['meter_number', 'meter_type', 'meter_status', 'consumer']
    list_filter = ['meter_type', 'meter_status']
    search_fields = ['meter_number', 'consumer__consumer_name']
