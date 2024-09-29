from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

# Custom manager for handling user creation
class UserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError("Users must have a username")
        
        # Normalize email (convert to lowercase)
        email = self.normalize_email(email)
        
        # Create user instance with extra fields and set password
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)  # Securely store the password
        else:
            user.set_unusable_password()  # For users who don't provide a password
        
        # Save user to the database
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None):
        # Create superuser with elevated permissions
        user = self.create_user(username=username, email=email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

# Custom User model inheriting from AbstractBaseUser and PermissionsMixin
class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    USERNAME_FIELD = 'email'
    # User roles
    is_sdo = models.BooleanField(default=False)  # Superuser role
    is_office_staff = models.BooleanField(default=False)  # Office staff role
    is_meter_reader = models.BooleanField(default=False)  # Meter reader role
    is_consumer = models.BooleanField(default=False)  # Consumer role
    
    # Staff status for Django admin purposes
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  # Set to False if user is deactivated

    # Manager for the User model
    objects = UserManager()

    # Set username as the login field
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']  # Superusers must have an email

    # String representation of the user
    def __str__(self):
        return self.username

    # Role-based methods for convenience
    @property
    def role(self):
        if self.is_sdo:
            return 'SDO'
        elif self.is_office_staff:
            return 'Office Staff'
        elif self.is_meter_reader:
            return 'Meter Reader'
        elif self.is_consumer:
            return 'Consumer'
        return 'Unknown'
