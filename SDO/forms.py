# forms.py
from django import forms
from .models import Tariff

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = ['tariff_type', 'price_100', 'price_200', 'price_300', 'price_above']
