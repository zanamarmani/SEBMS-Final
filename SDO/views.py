from django.shortcuts import redirect, render,get_object_or_404

# Create your views here.
from django.utils.crypto import get_random_string

from users.models import User
from django.contrib import messages

from .models import Tariff
from .forms import TariffForm

from consumer.models import Consumer
from users.forms import UserForm
def dashboard(request):
    return render(request, 'sdo/dashboard.html')


def create_office_staff(request):
    if request.method == "POST":
        reference_number = get_random_string(8)
        password = 'officestaff'
        new_office_staff = User.objects.create_user(
            username=reference_number, password=password, is_office_staff=True
        )
        # Optional: Add a success message
        messages.success(request, f"Office staff created with reference number {reference_number} and default password.")
        return redirect('SDO:dashboard')
    return render(request, 'sdo/create_office_staff.html')

def admin_dashboard(request):
    return render(request, 'sdo/admin_dashboard.html')

def approve_new_consumers(request):
    consumers = Consumer.objects.filter(approved=False)
    if request.method == 'POST':
        consumer_id = request.POST.get('consumer_id')
        consumer = Consumer.objects.get(id=consumer_id)
        consumer.approved = True
        consumer.save()
        return redirect('SDO:approve_new_consumers')
    return render(request, 'sdo/approve_new_consumers.html', {'consumers': consumers})

def reject_new_consumers(request):
    if request.method == 'POST' and request.POST.get('action') == 'reject':
        consumer_id = request.POST.get('consumer_id')
        consumer = get_object_or_404(Consumer, id=consumer_id)
        
        # Handle any additional logic for rejected consumers (e.g., deleting, marking as rejected)
        consumer.delete()  # Delete the consumer from the database
        
        return redirect('SDO:approve_new_consumers')  # Redirect back to the same page
    return render(request, 'sdo/approve_new_consumers.html', {'consumers': consumer})
    # return redirect('approve_new_consumers')

def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('SDO:show_all_users')
    else:
        form = UserForm()
    return render(request, 'sdo/add_user.html', {'form': form})

def show_all_consumers(request):
    consumers = Consumer.objects.all()
    return render(request, 'sdo/show_all_consumers.html', {'consumers': consumers})

def show_all_users(request):
    users = User.objects.all()
    return render(request, 'sdo/show_all_users.html', {'users': users})


def update_tariff(request):
    tariffs = Tariff.objects.all()  # Get all tariff types
    if request.method == 'POST':
        form = TariffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('SDO:update_tariff')  # Redirect back to tariff management page
    else:
        form = TariffForm()

    return render(request, 'sdo/update_tariff.html', {'form': form, 'tariffs': tariffs})
