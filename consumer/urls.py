from django.urls import path
from . import views

app_name = 'consumer'
urlpatterns = [
    path('', views.consumer_home, name='consumer_home'),
    path('pay_online/<int:bill_id>/', views.payment_gateway, name='payment_gateway'),
    path('jazzcash_payment/<int:bill_id>/', views.jazzcash_payment, name='jazzcash_payment'),
    path('payment_success/', views.payment_success, name='payment_success'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
    path('show_profile/', views.show_profile, name='show_profile'),
    path('update_profile/', views.update_profile, name='update_profile'),
    path('show_bills/', views.show_bills, name='show_bills'),
]