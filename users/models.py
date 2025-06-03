from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from hashlib import sha256


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin')
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    _cin = models.CharField(null=True,default='AB123456',unique=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name','role']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"




    @property
    def cin(self):
        return f"{self._cin[:2]}****{self._cin[-2:]}"    

    @cin.setter
    def cin(self,value):
        self._cin = value


class Patient(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    def clean(self):
        if self.user.role != 'patient':
            raise ValidationError("User must be a patient")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Doctor(models.Model):
    SPECIALITY_CHOICES = [
        ('cardiologist', 'Cardiologist'),
        ('neurologist', 'Neurologist')
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor'
    )
    speciality = models.CharField(max_length=15, choices=SPECIALITY_CHOICES)

    def get_full_name(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return f"Dr. {self.user.first_name} {self.user.last_name}"
    
    def clean(self):
        if self.user.role != 'doctor':
            raise ValidationError("User must be a doctor")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)