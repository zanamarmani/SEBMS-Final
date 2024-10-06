# utils.py (or wherever your utility functions are)
from .models import Tariff

# def calculate_bill(consumed_units, tariff_type):
#     try:
#         tariff = Tariff.objects.get(tariff_type=tariff_type)
#     except Tariff.DoesNotExist:
#         raise ValueError("Tariff not found. Please set the tariff in the SDO dashboard.")

#     # Initialize total bill
#     total_bill = 0
    
#     # Pricing tiers
#     price_tiers = [
#         (100, tariff.price_100),   # First 100 units
#         (100, tariff.price_200),   # Next 100 units (101-200)
#         (100, tariff.price_300),   # Next 100 units (201-300)
#         (float('inf'), tariff.price_above)  # Above 300 units
#     ]

#     # Calculate the bill based on consumed units and the price tiers
#     for limit, price_per_unit in price_tiers:
#         if consumed_units > limit:
#             total_bill += limit * price_per_unit
#             consumed_units -= limit
#         else:
#             total_bill += consumed_units * price_per_unit
#             break
    
#     return total_bill

# SDO/utils.py
def calculate_bill(consumed_units, tariff):
    # Check if a valid tariff exists
    if not tariff:
        raise ValueError("Tariff not found. Please set the tariff in the SDO dashboard.")

    # Initialize total bill
    total_bill = 0
    
    # Pricing tiers based on your Tariff model fields
    price_tiers = [
        (100, tariff.price_100),   # First 100 units
        (100, tariff.price_200),   # Next 100 units (101-200)
        (100, tariff.price_300),   # Next 100 units (201-300)
        (float('inf'), tariff.price_above)  # Above 300 units
    ]
    
    # Calculate the bill based on consumed units and the price tiers
    for limit, price_per_unit in price_tiers:
        if consumed_units > limit:
            total_bill += limit * price_per_unit
            consumed_units -= limit
        else:
            total_bill += consumed_units * price_per_unit
            break
    
    return total_bill

from django.http import JsonResponse
from bill.models import Bill  # Assuming you have a Bill model that tracks bills

def bills_data(request):
    total_bills = Bill.objects.all().count()
    paid_bills = Bill.objects.filter(paid=True).count()  # Assuming 'status' field exists

    data = {
        'total_bills': 100,
        'paid_bills': 50,
        'labels': ['Total Bills', 'Paid Bills']
    }

    return JsonResponse(data)