from django.db import models
from users.models import User
# Create your models here.
class Office_Staff_Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True , related_name='office_staff')
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    office_location = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    joining_date = models.DateField()
    