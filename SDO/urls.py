from django.urls import path, include
from .import views
app_name = 'SDO'
urlpatterns = [
    path('', views.dashboard, name='dashboard' ),
    path('create_office_staff/', views.create_office_staff, name='create_office_staff'),
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('approve_new_consumers/', views.approve_new_consumers, name='approve_new_consumers'),
    path('reject_new_consumers/', views.reject_new_consumers, name='reject_new_consumers'),
    path('add_user/', views.add_user, name='add_user'),
    path('show_all_consumers/', views.show_all_consumers, name='show_all_consumers'),
    path('show_all_users/', views.show_all_users, name='show_all_users'),
    path('update-tariff/<int:tariff_id>/', views.update_tariff, name='update_tariff'),
    path('all_bills/', views.all_bills ,name='all_bills'),
    path('paid_bills/', views.paid_bills, name='paid_bills'),
    path('unpaid_bills/', views.unpaid_bills, name='unpaid_bills'),
    path('show_users/', views.show_users,name='show_users'),
    
    
]

