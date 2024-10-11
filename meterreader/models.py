from django.db import models

from consumer.models import Consumer

class Meter(models.Model):
    METER_TYPE_CHOICES = [
        ('single', 'Single Phase'),
        ('double', 'Double Phase'),
        ('three', 'Three Phase'),
    ]
    
    meter_number = models.CharField(max_length=100,null=True,unique=True)  # Meter number
    new_reading = models.DecimalField(max_digits=10, decimal_places=2,null=True)  # New meter reading
    last_reading = models.DecimalField(max_digits=10, decimal_places=2,null=True)  # Last meter reading
    meter_type = models.CharField(max_length=10, choices=METER_TYPE_CHOICES, null=True)
    meter_status = models.BooleanField(default=True,null=True)  # Active (True) or Not (False)
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE,null=True)  # Many-to-one to Consumer
    processed = models.BooleanField(default=False,null=True) 
    reading_date = models.DateField(null=True)

    def __str__(self):
        return self.meter_number
