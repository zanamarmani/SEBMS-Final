from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse
from SDO.models import Tariff
from consumer.models import Consumer
from meterreader.models import MeterReading
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from users.models import User

from bill.models import Bill, Bill_Details
from SDO.utills import calculate_bill
from datetime import date

from .fire_base_utils import fetch_meter_readings

def Home(request):
    consumers = Consumer.objects.all()  # Fetch all consumers from the database
    return render(request, 'officeStaffHome.html', {'consumers': consumers})
    
def RegisterConsumer(request):
    return render(request, 'RegisterConsumer.html')
# officeStaff/views.py


def register_consumer(request):
    if request.method == 'POST':
        # Collect form data
        password = request.POST.get('password')
        name = request.POST.get('name')
        consumer_number = request.POST.get('consumer_number')
        meter_number = request.POST.get('meter_number')
        area_number = request.POST.get('area_number')
        tariff_type = request.POST.get('tariff')  # Get the selected tariff type from the form

        # Check if a User with this email already exists
        if User.objects.filter(email=consumer_number + '@gmail.com').exists():
            return HttpResponse('A user with this consumer number already exists. Please use a different consumer number.')

        # Create a User object
        user = User.objects.create_user(email=consumer_number + '@gmail.com', password=password, is_consumer=True)

        # Fetch the selected Tariff object
        tariff = get_object_or_404(Tariff, tariff_type=tariff_type)

        # Create the Consumer object, associating it with the created User and selected Tariff
        consumer = Consumer(
            user=user,
            name=name,
            consumer_number=consumer_number,
            meter_number=meter_number,
            area_number=area_number,
            tariff=tariff,  # Assign the tariff to the consumer
        )

        consumer.save()  # Save the Consumer to the database

        return HttpResponse('Registered successfully.')  # Redirect to a success page or home page

    # Pass the available tariffs to the template for selection in the form
    tariffs = Tariff.objects.all()
    return render(request, 'register_consumer.html', {'tariffs': tariffs}) 

def list_consumers(request):
    consumers = Consumer.objects.all()
    return render(request, 'list_consumers.html', {'consumers': consumers})


def all_readings(request):
    """
    View to display all readings and their corresponding bills.
    """
    readings = MeterReading.objects.all()
    bills = []

    for reading in readings:
        consumer = Consumer.objects.filter(meter_number=reading.meter_number).first()
        if consumer:
            # Fetch the existing bill for this consumer and the current month
            current_month = timezone.now().date().replace(day=1)
            bill = Bill.objects.filter(consumer=consumer, month=current_month).first()

            # Append the reading and the existing bill as a tuple for display
            bills.append((reading, bill))

    return render(request, 'all_readings.html', {'bills': bills})
def generate_bill(request, meter_number):
    """
    View to generate a bill for a specific consumer based on meter readings.
    """
    consumer = get_object_or_404(Consumer, meter_number=meter_number)
    reading = MeterReading.objects.filter(meter_number=meter_number).last()  # Get the latest reading

    if not reading:
        messages.error(request, "No meter reading found for this consumer.")
        return redirect('officestaff:consumer_list')

    consumed_units = reading.new_reading - reading.last_reading
    if consumed_units < 0:
        messages.error(request, "Consumed units cannot be negative. Please check meter readings.")
        return redirect('officestaff:consumer_list')

    # Get the consumer's tariff and calculate the bill
    tariff = Tariff.objects.filter(tariff_type=consumer.tariff).first()
    if not tariff:
        messages.error(request, "Tariff not found for this consumer.")
        return redirect('officestaff:list_consumers')

    bill_amount = calculate_bill(consumed_units, tariff)

    # Create a new Bill entry for the current month
    bill = Bill.objects.create(
        consumer=consumer,
        month=date.today(),  # Current month
        amount_due=bill_amount,
        consumed_units=consumed_units,
        paid=False
    )

    messages.success(request, f'Bill for consumer {consumer.name} has been generated successfully!')
    return redirect('officestaff:all_readings')

def Get_All_Readings(request):
    # Fetch meter readings from Firebase
    meter_readings = fetch_meter_readings()
    # Fetch all bills to display on the dashboard
    return render(request, 'officestaff/dashboard.html', {'meter_readings': meter_readings})