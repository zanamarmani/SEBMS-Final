from django import forms
from .models import MeterReading

class MeterReadingForm(forms.ModelForm):
    class Meta:
        model = MeterReading
        fields = ['meter_number', 'last_reading', 'new_reading', 'reading_date']
