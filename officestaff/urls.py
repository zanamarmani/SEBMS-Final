from django.urls import path

from . import views

urlpatterns = [
    path("office-staff/me/", views.OfficeStaffMeView.as_view(), name="office-staff-me"),
]
