from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['bill', 'reference', 'amount', 'status', 'bank_charges', 'arrears_charges', 'created_at']
    list_filter = ['status']
    search_fields = ['reference', 'bill__meter__meter_number']
