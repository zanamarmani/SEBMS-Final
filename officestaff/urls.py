
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
app_name = 'officestaff'
urlpatterns = [
    path('',views.Home, name = 'home'),
    path('register_consumer/', views.RegisterConsumer, name='registerconsumer'),
    path('registerconsumer/', views.register_consumer, name='register_consumer'),
    path('consumers/', views.list_consumers, name='list_consumers'),
    path('all_readings/', views.Get_All_Readings, name='all_readings'),
    path('generate-bill/<str:meter_number>/', views.generate_bill, name='generate_bill'),
    path('save_meter_data/', views.save_meter_data_to_db, name='save_meter_data'),
]
