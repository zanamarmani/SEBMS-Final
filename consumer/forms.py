from django import forms
from .models import Consumer
from SDO.models import Tariff

class ConsumerForm(forms.ModelForm):
    # Creating a select dropdown for Tariff
    tariff = forms.ModelChoiceField(
        queryset=Tariff.objects.all(),
        empty_label="Select Tariff",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Consumer
        fields = ['name', 'consumer_number', 'meter_number', 'area_number', 'tariff']  # 'approved' field removed from form
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter name'}),
            'consumer_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter consumer number'}),
            'meter_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter meter number'}),
            'area_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter area number'}),
        }

    def save(self, commit=True):
        # Create a Consumer instance, but don't save it yet
        consumer = super().save(commit=False)
        
        # Set approved to False
        consumer.approved = False
        
        # Save the Consumer instance
        if commit:
            consumer.save()

        return consumer
