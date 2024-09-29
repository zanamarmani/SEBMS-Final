from django.urls import path
from . import views
urlpatterns = [
    path('',views.home, name = 'home'),  
    path('submit_reading/',views.submit_reading, name = 'submit_reading'),
    path('success/', views.success, name='success'),
    path('submit_reading/', views.submit_reading, name='submit_reading'),
    path('delete_reading/<int:reading_id>/', views.delete_reading, name='delete_reading'),
]