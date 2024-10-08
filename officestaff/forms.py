from django import forms
from consumer.models import Consumer

class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ['name', 'consumer_number', 'meter_number', 'area_number', 'tariff']

from django import forms
from .models import Office_Staff_Profile

class OfficeStaffProfileForm(forms.ModelForm):
    class Meta:
        model = Office_Staff_Profile
        fields = ['name', 'designation', 'office_location', 'contact_number', 'joining_date']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Designation'}),
            'office_location': forms.TextInput(attrs={'placeholder': 'Office Location'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Contact Number'}),
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(OfficeStaffProfileForm, self).__init__(*args, **kwargs)
        # You can customize further initializations if needed
