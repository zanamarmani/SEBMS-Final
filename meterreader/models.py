from django.db import models

class MeterReading(models.Model):
    meter_number = models.CharField(max_length=100)
    last_reading = models.IntegerField()
    new_reading = models.IntegerField()
    reading_date = models.DateField()
    processed = models.BooleanField(default=False)
    def __str__(self):
        return f"Meter {self.meter_number} - {self.reading_date}"
