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
        email = self.cleaned_data['consumer_number'] + "@example.com"  # Generate email based on consumer number or set appropriately
        password = self.cleaned_data['password']
        user = User.objects.create_user(email=email, password=password, is_consumer=True)
        
        # Link the user to the consumer
        consumer.user = user

        if commit:
            consumer.save()
        return consumer
