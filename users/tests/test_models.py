import pytest
from django.core.exceptions import ValidationError
from django.db import models

from users.models import User, Patient, Doctor, CustomUserManager
from main.models import Appointment

from model_bakery import baker
from django.utils import timezone


@pytest.fixture
def doctor_instance():
    user = baker.make(User, _cin='AA909090', role='doctor', is_staff=True)
    doctor = baker.make(Doctor, user=user, speciality='cardiologist')
    return doctor

@pytest.fixture
def patient_instance():
    user = baker.make(User, _cin='BB909090', role='patient')
    patient = baker.make(Patient, user=user)
    return patient


@pytest.mark.django_db
def test_user_model_count():
    user = baker.make(User)
    assert User.objects.count() == 1 

@pytest.mark.django_db
def test_patient_model_count():
    user = baker.make(User, role='patient')
    assert Patient.objects.count() == 0 
    patient = baker.make(Patient, user=user)
    assert Patient.objects.count() == 1

@pytest.mark.django_db
def test_doctor_model_count():
    user = baker.make(User, role='doctor')
    doctor = baker.make(Doctor, user=user, speciality='neurologist') 
    assert Doctor.objects.count() == 1

@pytest.mark.django_db
def test_appointment_model_creation(patient_instance, doctor_instance):
    appointment = baker.make(Appointment, patient=patient_instance, doctor=doctor_instance)
    assert appointment.patient.user.id == patient_instance.user.id
    assert appointment.doctor.user.id == doctor_instance.user.id
    assert Appointment.objects.count() == 1


@pytest.mark.django_db
def test_custom_user_manager_create_user():
    user = User.objects.create_user(
        email="test@user.com",
        password="testpassword",
        first_name="Test",
        last_name="User"
    )
    assert user.email == "test@user.com"
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.check_password("testpassword")
    assert not user.is_staff
    assert not user.is_superuser
    assert user.is_active
    assert user.role == 'patient'
    assert User.objects.count() == 1

@pytest.mark.django_db
def test_custom_user_manager_create_superuser():
    superuser = User.objects.create_superuser(
        email="admin@example.com",
        password="adminpassword",
        first_name="Admin",
        last_name="User"
    )
    assert superuser.email == "admin@example.com"
    assert superuser.check_password("adminpassword")
    assert superuser.is_staff
    assert superuser.is_superuser
    assert superuser.is_active
    assert superuser.role == 'admin'
    assert User.objects.count() == 1

@pytest.mark.django_db
def test_custom_user_manager_create_user_no_email():
    with pytest.raises(ValueError, match="Users must have an email address"):
        User.objects.create_user(email="", password="password")



@pytest.mark.django_db
def test_user_str_method():
    user = baker.make(User, first_name="John", last_name="Doe")
    assert str(user) == "John Doe"

@pytest.mark.django_db
def test_user_email_unique():
    baker.make(User, email="unique@example.com")
    with pytest.raises(Exception):
        baker.make(User, email="unique@example.com")



@pytest.mark.django_db
def test_patient_str_method(patient_instance):
    assert str(patient_instance) == f"{patient_instance.user.first_name} {patient_instance.user.last_name}"


@pytest.mark.django_db
def test_patient_clean_method_invalid_role():
    user_with_doctor_role = baker.make(User, role='doctor')
    patient = Patient(user=user_with_doctor_role)
    with pytest.raises(ValidationError, match="User must be a patient"):
        patient.full_clean()

@pytest.mark.django_db
def test_patient_save_method_calls_clean():
    user_with_doctor_role = baker.make(User, role='doctor')
    patient = Patient(user=user_with_doctor_role)
    with pytest.raises(ValidationError, match="User must be a patient"):
        patient.save()



@pytest.mark.django_db
def test_doctor_str_method(doctor_instance):
    assert str(doctor_instance) == f"Dr. {doctor_instance.user.first_name} {doctor_instance.user.last_name}"

@pytest.mark.django_db
def test_doctor_get_full_name_method(doctor_instance):
    assert doctor_instance.get_full_name() == f"Dr. {doctor_instance.user.first_name} {doctor_instance.user.last_name}"


@pytest.mark.django_db
def test_appointment_str_method(patient_instance, doctor_instance):
    appointment = baker.make(
        Appointment,
        patient=patient_instance,
        doctor=doctor_instance,
        date_scheduled=timezone.now() + timezone.timedelta(days=1)
    )
    expected_str_part = f"Appointment for {patient_instance} with {doctor_instance}"
    assert expected_str_part in str(appointment)

@pytest.mark.django_db
def test_appointment_cancel_method(patient_instance, doctor_instance):
    appointment = baker.make(
        Appointment,
        patient=patient_instance,
        doctor=doctor_instance,
        status='scheduled',
        date_scheduled=timezone.now() + timezone.timedelta(days=1)
    )
    assert appointment.status == 'scheduled'
    appointment.cancel()
    assert appointment.status == 'cancelled'

@pytest.mark.django_db
def test_appointment_confirm_method(patient_instance, doctor_instance):
    appointment = baker.make(
        Appointment,
        patient=patient_instance,
        doctor=doctor_instance,
        status='scheduled',
        date_scheduled=timezone.now() + timezone.timedelta(days=1)
    )
    assert appointment.status == 'scheduled'
    appointment.confirm()
    assert appointment.status == 'confirmed'

@pytest.mark.django_db
def test_appointment_complete_method(patient_instance, doctor_instance):
    appointment = baker.make(
        Appointment,
        patient=patient_instance,
        doctor=doctor_instance,
        status='confirmed',
        date_scheduled=timezone.now() + timezone.timedelta(days=1)
    )
    assert appointment.status == 'confirmed'
    appointment.complete()
    assert appointment.status == 'completed'
    