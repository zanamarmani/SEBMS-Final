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

def Home(request):
    consumers = Consumer.objects.all()  # Fetch all consumers from the database
    return render(request, 'officeStaffHome.html', {'consumers': consumers})
    
def RegisterConsumer(request):
    return render(request, 'RegisterConsumer.html')
# officeStaff/views.py


def register_consumer(request):
    if request.method == 'POST':
        # Assuming you're getting these fields from the form
        password = request.POST.get('password')
        name = request.POST.get('name')
        consumer_number = request.POST.get('consumer_number')
        meter_number = request.POST.get('meter_number')
        area_number = request.POST.get('area_number')
        tariff = request.POST.get('tariff')

        # Check if a User with this username already exists
        if User.objects.filter(username=consumer_number).exists():
            return HttpResponse('A user with this consumer number already exists. Please use a different consumer number.')

        # Create a User object
        user = User.objects.create_user(username=consumer_number, password=password, is_consumer=True)
        
        # Now create the Consumer object, associating it with the created User
        consumer = Consumer(
            user=user,
            name=name,
            consumer_number=consumer_number,
            meter_number=meter_number,
            area_number=area_number,
            tariff=tariff
        )
        
        consumer.save()  # Save the Consumer to the database
        
        return HttpResponse('Registered successfully.')  # Redirect to a success page or home page

    return render(request, 'register_consumer.html')  # Render the registration form


def list_consumers(request):
    consumers = Consumer.objects.all()
    return render(request, 'list_consumers.html', {'consumers': consumers})


def all_readings(request): 
    readings = MeterReading.objects.all()
    bills = []

    for reading in readings:
        consumer = Consumer.objects.filter(meter_number=reading.meter_number).first()
        if consumer:
            consumed_units = reading.new_reading - reading.last_reading
            # Get the consumer's tariff object
            tariff = Tariff.objects.filter(tariff_type=consumer.tariff).first()

            if tariff:
                # Calculate the bill based on the tariff
                amount_due = calculate_bill(consumed_units, tariff)

                # Get the first day of the current month
                current_month = timezone.now().date().replace(day=1)

                # Check if a bill for this consumer and month already exists
                bill, created = Bill.objects.update_or_create(
                    consumer=consumer,
                    month=current_month,
                    defaults={'amount_due': amount_due, 'consumed_units': consumed_units}
                )
                
                # Append both the reading and the bill as a tuple
                bills.append((reading, bill))

    return render(request, 'all_readings.html', {'bills': bills})

def generate_bill(request, meter_number):
    # Fetch the consumer object
    consumer = get_object_or_404(Consumer, meter_number=meter_number)
    
    # You should retrieve the meter readings here.
    # For this example, assume we have consumed units and last reading.
    # You can fetch these from your `MeterReading` model or directly calculate them.
    readings = MeterReading.objects.all()
    for reading in readings:
        consumer = Consumer.objects.filter(meter_number=reading.meter_number).first()
        if consumer:
            consumed_units = reading.new_reading - reading.last_reading

    if consumed_units < 0:
        messages.error(request, "Consumed units cannot be negative. Please check meter readings.")
        return redirect('officestaff:consumer_list')  # Redirect to the list of consumers or another page

    # Fetch the tariff type for the consumer (domestic, commercial, etc.)
    tariff_type = Tariff.objects.filter(tariff_type=consumer.tariff).first()

    # Calculate the bill using the updated tariff structure
    bill_amount = calculate_bill(consumed_units, tariff_type)
    
    # Create a new Bill entry
    bill = Bill.objects.create(
        consumer=consumer,
        month=date.today(),  # Set the current date as the bill month
        amount_due=bill_amount,
        consumed_units=consumed_units,
        paid=False  # Set to False initially, to be updated upon payment
    )

    # Create a new Bill_Details entry (optional, if you need detailed breakdown)
    # Bill_Details.objects.create(
    #     consumer_no=consumer.consumer_number,
    #     meter_no=consumer.meter_number,
    #     new_reading=new_reading,
    #     last_reading=last_reading,
    #     Date_of_Reading=date.today(),
    #     bill_amount=bill_amount,
    #     due_date=date.today()  # Set due date as required
    # )

    # Add a success message and redirect to another page
    messages.success(request, f'Bill for consumer {consumer.name} has been generated successfully!')
    return redirect('officestaff:all_readings')  # Redirect to the bill list page or another page
