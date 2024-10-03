from django.shortcuts import render

# Create your views here.


from django.http import HttpResponse
from SDO.models import Tariff
from consumer.forms import ConsumerForm
from consumer.models import Consumer
from meterreader.models import MeterReading
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib import messages
from users.models import User

from bill.models import Bill, Bill_Details
from SDO.utills import calculate_bill
from datetime import datetime

from .firebase_utils import fetch_meter_list 

def Home(request):
    consumers = Consumer.objects.all()  # Fetch all consumers from the database
    return render(request, 'officeStaffHome.html', {'consumers': consumers})
    
def RegisterConsumer(request):
    return render(request, 'RegisterConsumer.html')
# officeStaff/views.py


def register_consumer(request):
    if request.method == 'POST':
        form = ConsumerForm(request.POST)
        if form.is_valid():
            form.save()  # Save the consumer to the database with approved set to False
            return HttpResponse('successfully send request to  register consumer')  # Redirect to a success page
    else:
        form = ConsumerForm()

    return render(request, 'register_consumer_try.html', {'form': form})

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
    meter_readings = fetch_meter_list()
    # Fetch all bills to display on the dashboard
    return render(request, 'all_reading_tryy.html', {'meter_readings': meter_readings})

def save_meter_data_to_db(request):
    """
    Fetch the meter data from Firebase and save it to the local database.
    """
    # Fetch meter data from Firebase
    meter_data_list = fetch_meter_list()

    # Process and save each meter reading into the local database
    for meter_data in meter_data_list:
        meter_id = meter_data.get('id', None)
        date_str = meter_data.get('date', None)
        serial_no = meter_data.get('serial_no', '')
        reading = meter_data.get('reading', '')

        # Convert date from string to Python date object
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        try:
            reading = float(reading)  # Convert the reading to float
        except ValueError:
            # Handle the case where the reading cannot be converted
            continue
        reading = int(round(reading))
        # Save or update the meter data in the database
        if meter_id and date_obj:
            MeterReading.objects.update_or_create(
                defaults={
                    'meter_number': serial_no,
                    'last_reading': 400,
                    'new_reading': reading,
                    'reading_date': date_obj
                }
            )

    # After saving, retrieve the saved data to display it
    meter_list = MeterReading.objects.all()

    # Render the template with the saved meter data
    return render(request, 'meter_data.html', {'meter_list': meter_list})

# views.py

from django.views.generic import ListView

class TariffListView(ListView):
    model = Tariff
    template_name = 'register_consumer.html'  # Path to your template
    context_object_name = 'tariffs'  # This will be the name of the variable in your template

    def get_queryset(self):
        return Tariff.objects.all()
