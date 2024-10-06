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
from datetime import date, datetime
from django.core.mail import send_mail


from .firebase_utils import fetch_meter_list 

def Home(request):
    consumers = Consumer.objects.all()  # Fetch all consumers from the database
    return render(request, 'officeStaffHome.html', {'consumers': consumers})
    
def RegisterConsumer(request):
    tariffs=Tariff.tariff_type
    return render(request, 'RegisterConsumer.html',{'tariffs':tariffs})
# officeStaff/views.py


def register_consumer(request):
    if request.method == 'POST':
        form = ConsumerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Consumer registered successfully.")
            return redirect('officestaff:registerconsumer')  # Redirect to the same page after successful registration
        else:
            messages.error(request, "Error in registration. Please check the form.")
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
            bills = Bill.objects.filter(consumer=consumer, month=current_month).first()

            # Append the reading and the existing bill as a tuple for display
            bills.append((reading, bills))

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
    return render(request, 'all_readings.html', {'meter_readings': meter_readings})

def save_meter_data_to_db(request):
    """
    Fetch the meter data from Firebase and save it to the local database.
    """
    # Fetch meter data from Firebase
    meter_data_list = fetch_meter_list()

    # Process and save each meter reading into the local database
    for meter_data in meter_data_list:
        meter_id = meter_data.get('id', None)  # Unique meter ID from Firebase
        date_str = meter_data.get('date', None)  # Date string
        serial_no = meter_data.get('serial_no', '')  # Serial number of the meter
        reading = meter_data.get('reading', '')  # Meter reading value

        # Convert date from string to Python date object
        if date_str:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        try:
            reading = float(reading)  # Convert the reading to float
        except ValueError:
            continue  # Skip this entry if reading is invalid

        reading = int(round(reading))  # Round and convert to integer

        # Retrieve the last reading for this meter using filter() and order by the most recent reading
        last_reading_record = MeterReading.objects.filter(meter_number=serial_no).order_by('-reading_date').first()

        if last_reading_record:
            last_reading = last_reading_record.new_reading  # Use the most recent `new_reading`
        else:
            last_reading = 500  # Default last reading if no previous record exists

        # Use get_or_create to avoid IntegrityError for unique meter_number
        meter_reading, created = MeterReading.objects.get_or_create(
            meter_number=serial_no,
            defaults={
                'last_reading': last_reading,
                'new_reading': reading,
                'reading_date': date_obj
            }
        )

        if not created:
            # If the record already exists, update it
            meter_reading.last_reading = last_reading
            meter_reading.new_reading = reading
            meter_reading.reading_date = date_obj
            meter_reading.save()

    # After saving, retrieve the saved data to display it
    meter_list = MeterReading.objects.all()

    # Render the template with the saved meter data
    return render(request, 'all_readings.html', {'meter_list': meter_list})

# views.py
def all_bills(request):
    # Fetch all bills from the database
    bills = Bill.objects.all()
    return render(request, 'all_bills.html', {'bills': bills})

def paid_bills(request):
    # Fetch paid bills from the database
    bills = Bill.objects.filter(paid=True)
    return render(request, 'paid_bills.html', {'paid_bills': bills})

def unpaid_bills(request):
    # Fetch unpaid bills from the database
    bills = Bill.objects.filter(paid=False)
    return render(request, 'unpaid_bills.html', {'unpaid_bills': bills})
from django.views.generic import ListView

class TariffListView(ListView):
    model = Tariff
    template_name = 'register_consumer.html'  # Path to your template
    context_object_name = 'tariffs'  # This will be the name of the variable in your template

    def get_queryset(self):
        return Tariff.objects.all()
def Generate_bill(request):
    """
    View to generate a bill for a specific consumer based on meter readings.
    """
    readings = MeterReading.objects.filter(processed=False)  # Get all unprocessed readings
    for reading in readings:
        # Step 2: Find the associated consumer using the meter number
        try:
            consumer = Consumer.objects.get(meter_number=reading.meter_number)
        except Consumer.DoesNotExist:
            continue  # Skip if no matching consumer found

        # Step 3: Calculate the consumed units
        consumed_units = reading.new_reading - reading.last_reading

        # Step 4: Get the tariff details associated with the consumer
        tariff = consumer.tariff

        # Step 5: Calculate the bill amount
        bill_amount = calculate_bill(consumed_units, tariff)

        # Step 6: Create a new bill entry for the current month
        try:
            bill = Bill.objects.create(
                consumer=consumer,
                month=date.today(),  # Current month
                amount_due=bill_amount,
                consumed_units=consumed_units,
                paid=False
            )
            reading.processed = True  # Mark the reading as processed
            reading.save()  # Save the changes to the database
            if bill:
                send_mail(
                    'Bill Generation',
                    f'Your bill for {consumer.name} is due on {bill.month}. Amount due: {bill.amount_due}',
                    'zanam786armani@gmail.com',
                    [consumer.email],
                    fail_silently=False,
                )
        except Exception as e:
            print(f"Error occurred while generating bill for consumer {consumer.name}: {str(e)}")
            continue  # Skip to the next consumer if there's an error

    # Move the success message and redirect outside the loop
    # messages.success(request, 'Bills have been generated successfully!')
    # return redirect('officestaff:all_readings')

    readings1 = MeterReading.objects.filter(processed=True)
    return render(request, 'all_readings.html', {'meter_list': readings1})