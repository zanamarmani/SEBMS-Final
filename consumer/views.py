from datetime import timedelta, timezone
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Consumer
from bill.models import Bill, Payment

@login_required
def consumer_home(request):
    consumer = get_object_or_404(Consumer, user=request.user)  # Get the consumer linked to the logged-in user
    status = consumer.approved
    # Fetch the consumer's bills and payment history
    bills = Bill.objects.filter(consumer=consumer)
    for bill in bills:
        bill.due_date = bill.month + timedelta(days=10)
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
        return render(request, 'consumerHome.html', {'consumer': consumer, 'status': status , 'bills':bills})  # Render the consumer home page with the consumer's profile information and status

def payment_gateway(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    return render(request, 'pay_online.html', {'bill': bill})



import hashlib
import requests
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponseRedirect

def generate_hash(merchant_id, password, integrity_salt, amount, order_ref):
    string_to_hash = f"{merchant_id}:{password}:{amount}:{order_ref}:{integrity_salt}"
    return hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()

def jazzcash_payment(request, bill_id):
    bill = get_object_or_404(Bill, id=bill_id)
    consumer = bill.consumer
    amount = bill.amount_due
    order_ref = str(bill.id) + str(timezone.now().timestamp())
    merchant_id = settings.JAZZCASH_MERCHANT_ID
    password = settings.JAZZCASH_PASSWORD
    integrity_salt = settings.JAZZCASH_INTEGRITY_SALT
    
    hash = generate_hash(merchant_id, password, integrity_salt, amount, order_ref)
    
    # JazzCash API URL
    jazzcash_url = "https://sandbox.jazzcash.com.pk/CustomerPortal/API/PaymentRequest.php"
    
    payload = {
        "pp_MerchantID": merchant_id,
        "pp_Password": password,
        "pp_Amount": amount * 100,  # JazzCash expects amount in Paisas
        "pp_TxnRefNo": order_ref,
        "pp_Description": f"Bill Payment for {consumer.consumer_number}",
        "pp_ReturnURL": "http://127.0.0.1:8000/payment_success/",  # Replace with your success URL
        "pp_SecureHash": hash,
    }
    
    response = requests.post(jazzcash_url, data=payload)
    
    if response.status_code == 200:
        return HttpResponseRedirect(response.json().get('pp_AuthURL'))
    else:
        return render(request, 'payment_failed.html', {'error': response.text})


from django.shortcuts import render
from django.http import HttpResponse

def payment_success(request):
    # Update bill status based on returned transaction details
    return render(request, 'payment_success.html')

def payment_failed(request):
    # Show an error page
    return render(request, 'payment_failed.html')
