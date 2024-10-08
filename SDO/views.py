from django.db import IntegrityError
from django.http import HttpResponse
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

from django.contrib.auth.decorators import login_required


def dashboard(request):
    tariff = Tariff.objects.first()  # or use a specific filter to fetch tariff
    consumers = Consumer.objects.count()

    # Count total office staff (assuming 'office_staff' is a role in the User model)
    office_staffs = User.objects.filter(is_office_staff = True).count()
    users = User.objects.count()
    # Count total meter readers (assuming 'meter_reader' is a role in the User model)
    meter_readers = User.objects.filter(is_meter_reader=True).count()
    return render(request, 'sdo/dashboard.html', {'tariff': tariff,'consumers':consumers,'total_office_staff':office_staffs,'total_users':users,'total_meter_reader':meter_readers})


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
    return render(request,
 'sdo/show_all_users.html', {'users': users})



def update_tariff(request, tariff_id=None):
    # Fetch all tariffs for display
    all_tariffs = Tariff.objects.all()

    # If a tariff_id is provided, try to fetch the specific tariff
    if tariff_id:
        tariff = Tariff.objects.filter(id=tariff_id).first()  # Use filter().first() to avoid 404 if not found
    else:
        tariff = None

    # Get tariff choices from the model
    tariff_choices = Tariff.TARIFF_CHOICES

    if request.method == 'POST':
        # Otherwise, process form for updating or creating the tariff
        tariff_type = request.POST.get('tariff_type')
        price_100 = request.POST.get('price_100')
        price_200 = request.POST.get('price_200')
        price_300 = request.POST.get('price_300')
        price_above = request.POST.get('price_above')

        # Try to create or update the tariff with the new values
        try:
            if tariff:
                # Update the existing tariff
                tariff.tariff_type = tariff_type
                tariff.price_100 = price_100
                tariff.price_200 = price_200
                tariff.price_300 = price_300
                tariff.price_above = price_above
                tariff.save()
                return HttpResponse("Tariff updated successfully.")
            else:
                # Create a new tariff
                new_tariff = Tariff(
                    tariff_type=tariff_type,
                    price_100=price_100,
                    price_200=price_200,
                    price_300=price_300,
                    price_above=price_above,
                )
                new_tariff.save()
                return HttpResponse("New tariff created successfully.")
        except IntegrityError:
            return HttpResponse("A tariff with this type already exists. Please choose a different type.")
        except ValueError:
            return HttpResponse("Invalid input. Please ensure all fields are filled out correctly.")

    # Render the update form with the current tariff values (if updating) and list of all tariffs
    return render(request, 'sdo/update_tariff.html', {
        'tariff': tariff,
        'tariff_choices': tariff_choices,
        'all_tariffs': all_tariffs,
    })



def all_bills(request):
    # Fetch all bills from the database
    bills = Bill.objects.all()
    return render(request, 'sdo/all_bills.html', {'bills': bills})

def paid_bills(request):
    # Fetch paid bills from the database
    bills = Bill.objects.filter(paid=True)
    return render(request, 'sdo/all_bills.html', {'bills': bills})

def unpaid_bills(request):
    # Fetch unpaid bills from the database
    bills = Bill.objects.filter(paid=False)
    return render(request, 'sdo/all_bills.html', {'bills': bills})


def sdo_dashboard_show_details(request):
    # Count total consumers
    total_consumers = Consumer.objects.all()

    # Count total office staff (assuming 'office_staff' is a role in the User model)
    office_staff = User.objects.filter(is_office_staff=True)

    # Count total meter readers (assuming 'meter_reader' is a role in the User model)
    meter_readers = User.objects.filter(is_meter_reader=True)

    return render(request, 'sdo/show_all_users.html',{'consumers': total_consumers,'office_staff': office_staff,'meter_readers': meter_readers})