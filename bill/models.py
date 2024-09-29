from django.db import models
from consumer.models import Consumer
# Create your models here.
# bill/models.py

class Bill_Details(models.Model):
    consumer_no = models.CharField(max_length=100,default=None)
    meter_no = models.CharField(max_length=100,default=None)
    new_reading = models.IntegerField
    last_reading = models.IntegerField
    Date_of_Reading = models.DateField
    bill_amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField

    def __str__(self):
        return f'{self.consumer_no} - {self.meter_no}'
class Bill(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    month = models.DateField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    consumed_units = models.IntegerField(default=None)

    def __str__(self):
        return f'{self.consumer} - {self.month}'

class Payment(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.consumer} - {self.amount_paid}'
