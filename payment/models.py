from django.db import models

from bill.models import Bill


class Payment(models.Model):
    class Status(models.TextChoices):
        INITIATED = 'initiated', 'Initiated'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, null=True)  # Foreign key to Bill
    reference = models.CharField(max_length=64, unique=True, null=True, blank=True)  # Gateway transaction ref
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Bank charges
    arrears_charges = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Arrears charges
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.INITIATED)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=['bill'], name='payment_bill_idx'),
            models.Index(fields=['status'], name='payment_status_idx'),
        ]

    def __str__(self):
        return f'Payment for Bill {self.bill_id}'
