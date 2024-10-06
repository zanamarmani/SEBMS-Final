from django.shortcuts import render
from consumer.models import Consumer
# Create your views here.

def calculate_bill(request):
    consumer_number = Consumer.objects.all()
    total_amount = 0
    for consumer in consumer_number:
        total_amount += consumer.amount_due
        # Here we need to calculate the bill for each consumer and add it to total_amount

    return render(request,'bill.html')

