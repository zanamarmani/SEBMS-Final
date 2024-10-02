from django.shortcuts import redirect, render,get_object_or_404

# Create your views here.
from django.utils.crypto import get_random_string

from bill.models import Bill
from users.models import User
from django.contrib import messages

from .models import Tariff
from .forms import TariffForm

from consumer.models import Consumer
from users.forms import UserForm
def dashboard(request):
    tariff = Tariff.objects.first()  # or use a specific filter to fetch tariff
    return render(request, 'sdo/dashboard.html', {'tariff': tariff})


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


from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from SDO.models import Tariff
from django.db import IntegrityError

def update_tariff(request, tariff_id):
    # Fetch the tariff object based on the ID
    tariff = get_object_or_404(Tariff, id=tariff_id)

    if request.method == 'POST':
        # Check if the form is being submitted for deletion
        if 'delete' in request.POST:
            # Delete the tariff
            tariff.delete()
            return HttpResponse("Tariff deleted successfully.")

        # Otherwise, process form for updating the tariff
        tariff_type = request.POST.get('tariff_type')
        price_100 = request.POST.get('price_100')
        price_200 = request.POST.get('price_200')
        price_300 = request.POST.get('price_300')
        price_above = request.POST.get('price_above')

        # Try updating the tariff with the new values
        try:
            tariff.tariff_type = tariff_type
            tariff.price_100 = price_100
            tariff.price_200 = price_200
            tariff.price_300 = price_300
            tariff.price_above = price_above
            tariff.save()
            return HttpResponse("Tariff updated successfully.")
        except IntegrityError:
            return HttpResponse("A tariff with this type already exists. Please choose a different type.")

    # Render the update form with the current tariff values
    return render(request, 'sdo/update_tariff.html', {'tariff': tariff})

def all_bills(request):
    # Fetch all bills from the database
    bills = Bill.objects.all()
    return render(request, 'sdo/all_bills.html', {'bills': bills})

def paid_bills(request):
    # Fetch paid bills from the database
    bills = Bill.objects.filter(paid=True)
    return render(request, 'sdo/paid_bills.html', {'bills': bills})

def unpaid_bills(request):
    # Fetch unpaid bills from the database
    bills = Bill.objects.filter(paid=False)
    return render(request, 'sdo/unpaid_bills.html', {'bills': bills})


def sdo_dashboard_show_details(request):
    # Count total consumers
    total_consumers = Consumer.objects.count()

    # Count total office staff (assuming 'office_staff' is a role in the User model)
    total_office_staff = User.objects.filter(role='office_staff').count()

    # Count total meter readers (assuming 'meter_reader' is a role in the User model)
    total_meter_readers = User.objects.filter(role='meter_reader').count()

    # Count total number of bills
    total_bills = Bill.objects.count()

    # Fetch all, paid, and unpaid bills for further display (from the previous request)
    all_bills = Bill.objects.all()
    paid_bills = Bill.objects.filter(is_paid=True)
    unpaid_bills = Bill.objects.filter(is_paid=False)

    # Pass all counts and bills to the template
    context = {
        'total_consumers': total_consumers,
        'total_office_staff': total_office_staff,
        'total_meter_readers': total_meter_readers,
        'total_bills': total_bills,
        'all_bills': all_bills,
        'paid_bills': paid_bills,
        'unpaid_bills': unpaid_bills,
    }

    return render(request, 'sdo/dashboard.html', context)