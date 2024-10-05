# consumer/models.py
from django.db import models
from users.models import User
from SDO.models import Tariff
class Consumer(models.Model):
    # Fields
    user = models.OneToOneField(User, null=True,on_delete=models.SET_NULL,related_name='consumer')  # Linking Consumer to User model
    name = models.CharField(max_length=100)  # Consumer's name
    consumer_number = models.CharField(max_length=100, unique=True)  # Unique consumer number
    meter_number = models.CharField(max_length=100, unique=True)  # Unique meter number
    area_number = models.CharField(max_length=100)  # Area number associated with the consumer
    tariff = models.ForeignKey(Tariff, on_delete=models.CASCADE,null=True) # Tariff type
    approved = models.BooleanField(default=False)  # Approval status for the consumer

    # String representation of the Consumer instance
    def __str__(self):
        return self.user.email if self.user else self.name

