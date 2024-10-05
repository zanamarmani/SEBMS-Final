
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
app_name = 'officestaff'
urlpatterns = [
    path('',views.Home, name = 'home'),
    path('register_consumer/', views.RegisterConsumer, name='register_consumer'),
    path('registerconsumer/', views.register_consumer, name='registerconsumer'),
    path('consumers/', views.list_consumers, name='list_consumers'),
    path('all_readings_from_firebase/', views.Get_All_Readings, name='all_readings_from_firebase'),
    path('all_readings/', views.all_readings, name='all_readings'),
    path('generate-bill/<str:meter_number>/', views.generate_bill, name='generate_bill'),
    path('save_meter_data/', views.save_meter_data_to_db, name='save_meter_data'),
    path('all_bills/', views.all_bills ,name='all_bills'),
    path('paid_bills/', views.paid_bills, name='paid_bills'),
    path('unpaid_bills/', views.unpaid_bills, name='unpaid_bills'),
    path('generate_bills/', views.Generate_bill, name='generate_bills'),
]
