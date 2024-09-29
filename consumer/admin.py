from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import  Consumer

@admin.register(Consumer)
class ConsumerAdmin(admin.ModelAdmin):
    list_display = ('user', 'consumer_number', 'meter_number', 'area_number', 'tariff')
    search_fields = ('user__username', 'consumer_number', 'meter_number')
    list_filter = ('tariff', 'area_number')


