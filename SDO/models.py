# consumer/models.py

from django.db import models

class Tariff(models.Model):
    # Define the different types of tariffs
    TARIFF_CHOICES = [
        ('domestic', 'Domestic'),
        ('commercial', 'Commercial'),
        ('industrial', 'Industrial'),
    ]
    
    tariff_type = models.CharField(max_length=10, choices=TARIFF_CHOICES, unique=True)
    
    # Fields to hold price tiers for each tariff
    price_100 = models.DecimalField(max_digits=10, decimal_places=2,default=3)  # Price for first 100 units
    price_200 = models.DecimalField(max_digits=10, decimal_places=2,default=4)  # Price for 100-200 units
    price_300 = models.DecimalField(max_digits=10, decimal_places=2,default=5)  # Price for 200-300 units
    price_above = models.DecimalField(max_digits=10, decimal_places=2,default=6)  # Price for units above 300
    
    def __str__(self):
        return self.get_tariff_type_display()  # Display readable name in admin

    class Meta:
        verbose_name_plural = 'Tariffs'
