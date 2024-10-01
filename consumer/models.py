# consumer/models.py
from django.db import models
from users.models import User

class Consumer(models.Model):
    # Choices for tariff types
    TARIFF_CHOICES = [
        ('domestic', 'Domestic'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
    ]

    # Fields
    user = models.OneToOneField(User, null=True,on_delete=models.CASCADE,related_name='consumer')  # Linking Consumer to User model
    name = models.CharField(max_length=100)  # Consumer's name
    consumer_number = models.CharField(max_length=100, unique=True)  # Unique consumer number
    meter_number = models.CharField(max_length=100, unique=True)  # Unique meter number
    area_number = models.CharField(max_length=100)  # Area number associated with the consumer
    tariff = models.CharField(max_length=10, choices=TARIFF_CHOICES)  # Tariff type
    approved = models.BooleanField(default=False)  # Approval status for the consumer

    # String representation of the Consumer instance
    def __str__(self):
        return self.user.username if self.user else self.name

