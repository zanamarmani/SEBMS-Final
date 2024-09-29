from django import forms
from django.contrib.auth.forms import UserCreationForm
from users.models import User

from .models import Tariff

class TariffForm(forms.ModelForm):
    class Meta:
        model = Tariff
        fields = '__all__'
class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'is_sdo', 'is_office_staff', 'is_meter_reader', 'is_consumer', 'is_active']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        
        # Add custom labels for role fields
        self.fields['is_sdo'].label = "SDO"
        self.fields['is_office_staff'].label = "Office Staff"
        self.fields['is_meter_reader'].label = "Meter Reader"
        self.fields['is_consumer'].label = "Consumer"
        
        # Customize widget attributes if needed (for example, making checkboxes)
        self.fields['is_sdo'].widget = forms.CheckboxInput()
        self.fields['is_office_staff'].widget = forms.CheckboxInput()
        self.fields['is_meter_reader'].widget = forms.CheckboxInput()
        self.fields['is_consumer'].widget = forms.CheckboxInput()

        # Optionally, you can set the username as a required field and other custom validation
        self.fields['username'].required = True
