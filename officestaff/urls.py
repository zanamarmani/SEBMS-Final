
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
app_name = 'officestaff'
urlpatterns = [
    path('',views.Home, name = 'home'),
    path('register_consumer/', views.RegisterConsumer, name='register_consumer'),
    path('registerconsumer/', views.register_consumer, name='registerconsumer'),
    path('consumers/', views.list_consumers, name='list_consumers'),
    path('all_readings/', views.all_readings, name='all_readings'),
    path('generate-bill/<str:meter_number>/', views.generate_bill, name='generate_bill'),
]
