from django.contrib import admin

# Register your models here.
from .models import MeterReading
@admin.register(MeterReading)
class Meter_reading(admin.ModelAdmin):
    list_display = ('meter_number', 'new_reading', 'last_reading', 'reading_date', 'processed')