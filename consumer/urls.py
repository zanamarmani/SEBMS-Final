from django.urls import path
from . import views

app_name = 'consumer'
urlpatterns = [
    path('', views.consumer_home, name='consumer_home'),
    path('payment_gateway/', views.payment_gateway, name='payment_gateway'),
]