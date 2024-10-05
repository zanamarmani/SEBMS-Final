from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm  # Use Django's built-in form
from django.urls import reverse  # To dynamically resolve URLs

def user_login(request):
    # Nested function to handle redirection based on user role
    def redirect_to_dashboard(user):
        if user.is_sdo:
            return redirect('SDO:dashboard')
        elif user.is_superuser:
            return redirect('admin:index')  # Redirect to admin dashboard if superuser
        elif user.is_office_staff:
            return redirect('officestaff:home')
        elif user.is_meter_reader:
            return redirect('meterreader:home')
        elif user.is_consumer:
            return redirect('consumer:consumer_home')
        else:
            return HttpResponse("User role not recognized. Please check user roles.")
    
    # If the request is POST, process the form
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect_to_dashboard(user)  # Redirect user based on role
            else:
                return render(request, 'users/login.html', {'form': form, 'error': 'Invalid username or password'})
        else:
            return render(request, 'users/login.html', {'form': form, 'error': 'Invalid form submission'})
    
    # If the request is GET, render the form
    else:
        form = AuthenticationForm()
        return render(request, 'users/login.html', {'form': form})
