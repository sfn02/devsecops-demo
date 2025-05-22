from django.forms import ModelForm
from django import forms
from .models import User,Patient
from main.models import Appointment
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class RegisterForm(ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password']
        extra_kwargs = {"password":{"write_only":True}}

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        try:
            user = super().save(commit=False)
            user.first_name = cleaned_data.get('first_name')
            user.last_name = cleaned_data.get('last_name')
            user.email = cleaned_data.get('email')
            validate_password(user=user,password=password)
        except ValidationError as error:
            self.add_error('password', error)
        return cleaned_data

    def save(self,commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'patient'
        user.is_staff = False
        if commit:
            user.save()
            Patient.objects.create(
                user=user
            )
        return user


class AppointmentForm(ModelForm):
    date_scheduled = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',  
            'class': 'form-control'
        })
    )

    class Meta:
        model = Appointment
        fields = ['reason', 'date_scheduled']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
        }