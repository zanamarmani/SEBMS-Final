# sdo_dashboard/context_processors.py
from .models import Tariff

def tariff_processor(request):
    # Get the first tariff or return None if no tariffs exist
    tariff = Tariff.objects.first()  
    return {'tariff': tariff}
