from django import forms
from consumer.models import Consumer

class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ['name', 'consumer_number', 'meter_number', 'area_number', 'tariff']
