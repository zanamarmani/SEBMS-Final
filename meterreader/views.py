from django.contrib import messages
from django.shortcuts import get_object_or_404, render
from meterreader.models import  MeterReading
# Create your views here.
from consumer.models import Consumer
def home(request):
    return render(request, 'dashboard.html')

from django.shortcuts import redirect
from .forms import MeterReadingForm

def success(request):
    return render(request, 'success.html')


def submit_reading(request):
    if request.method == 'POST':
        form = MeterReadingForm(request.POST)
        if form.is_valid():
            meter_number = form.cleaned_data['meter_number']  # Get the meter number from the form
            reading_date = form.cleaned_data['reading_date']  # Get the reading date from the form

            # Check if the meter number exists in the Consumer model
            if Consumer.objects.filter(meter_number=meter_number).exists():
                # Check if there is already a reading for this meter number on the same date
                existing_reading = MeterReading.objects.filter(meter_number=meter_number, reading_date=reading_date).first()
                if existing_reading:
                    # If a reading exists, display it and provide an option to delete it
                    messages.warning(request, f'Reading already exists for meter number {meter_number} on {reading_date}.')
                    return render(request, 'existing_reading.html', {'existing_reading': existing_reading, 'form': form})
                else:
                    # Save the new reading if no reading exists for the same date
                    form.save()
                    messages.success(request, 'Reading submitted successfully.')
                    return render(request, 'success.html')  # Render success page
            else:
                # Display an error message if the meter number does not exist
                messages.error(request, 'Meter number does not exist in the Consumer records.')
    else:
        form = MeterReadingForm()

    return render(request, 'take_reading.html', {'form': form})

def delete_reading(request, reading_id):
    # View to delete an existing reading
    reading = get_object_or_404(MeterReading, id=reading_id)
    reading.delete()
    messages.success(request, 'Reading deleted successfully. You can now enter a new reading.')
    return redirect('submit_reading')

