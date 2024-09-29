from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Consumer
from bill.models import Bill, Payment

@login_required
def consumer_home(request):
    consumer = get_object_or_404(Consumer, user=request.user)  # Get the consumer linked to the logged-in user
    status = consumer.approved
    # Fetch the consumer's bills and payment history
    if status:
        bills = Bill.objects.filter(consumer=consumer).order_by('-month')
        payments = Payment.objects.filter(consumer=consumer).order_by('-payment_date')
    
        context = {
        'consumer': consumer,  # Pass the consumer's profile information
        'bills': bills,  # Pass the consumer's bills
        'payments': payments,  # Pass the consumer's payment history
        }
        return render(request, 'consumerHome.html', context)
    else:
        return render(request, 'consumerHome.html', {'consumer': consumer, 'status': status})  # Render the consumer home page with the consumer's profile information and status

def payment_gateway(request):
    # Placeholder logic for the payment gateway
    return render(request, 'pay_online.html')