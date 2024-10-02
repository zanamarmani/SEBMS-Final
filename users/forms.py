from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

# User registration form
class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'is_office_staff', 'is_meter_reader', 'is_consumer', 'is_sdo']
        # You can customize labels if needed
        labels = {
            'email': 'Email Address',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user

# User login form
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label="Email")  # Override to use email instead of username

    class Meta:
        model = User
        fields = ['email', 'password']
