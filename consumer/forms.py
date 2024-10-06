from django import forms
from .models import Consumer
from users.models import User
from SDO.models import Tariff
class ConsumerForm(forms.ModelForm):
    # Password input for creating the User
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    
    class Meta:
        model = Consumer
        fields = ['name', 'consumer_number', 'meter_number', 'area_number', 'tariff']
        
    def save(self, commit=True):
        # Save the consumer instance
        consumer = super().save(commit=False)

        # Create and link a new User instance for the consumer
        email = self.cleaned_data['consumer_number'] + "@gmail.com"  # Generate email based on consumer number or set appropriately
        password = self.cleaned_data['password']
        user = User.objects.create_user(email=email, password=password, is_consumer=True)
        
        # Link the user to the consumer
        consumer.user = user

        if commit:
            consumer.save()
        return consumer

class ConsumerProfileForm(forms.ModelForm):
    class Meta:
        model = Consumer
        fields = ['name', 'consumer_number', 'meter_number', 'area_number', 'tariff']  # Exclude 'consumer_number' and 'meter_number'
    
    def __init__(self, *args, **kwargs):
        super(ConsumerProfileForm, self).__init__(*args, **kwargs)
        # Making consumer_number and meter_number read-only
        self.fields['consumer_number'] = forms.CharField(
            widget=forms.TextInput(attrs={'readonly': 'readonly'}),
            initial=self.instance.consumer_number
        )
        self.fields['meter_number'] = forms.CharField(
            widget=forms.TextInput(attrs={'readonly': 'readonly'}),
            initial=self.instance.meter_number
        )
        self.fields['tariff'] = forms.ModelChoiceField(
            queryset=Tariff.objects.all(),
            widget=forms.TextInput(attrs={'readonly': 'readonly'}),
            initial=self.instance.tariff
        )
        self.fields['area_number'] = forms.CharField(
            widget=forms.TextInput(attrs={'readonly': 'readonly'}),
            initial=self.instance.area_number
        )
