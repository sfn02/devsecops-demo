# main/urls.py
from django.urls import path
from .views import (PatientAppointmentListView, 
        AppointmentCreateView, 
        CancelAppointmentView,
        filter_doctors_by_speciality,
        DoctorAppointmentListView,
        DoctorUpdateAppointmentView,
        UserAppointmentsView,
        check_header)

urlpatterns = [
    path('patient/appointments/', PatientAppointmentListView.as_view(), name='patient_appointments'),
    path('patient/appointments/create/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('patient/appointments/<int:pk>/cancel/', CancelAppointmentView.as_view(), name='cancel_appointment'),
    # ------------------------
    path('doctor/filter-doctors/', filter_doctors_by_speciality.as_view(), name='filter_doctors_by_speciality'),
    path('doctor/appointments/', DoctorAppointmentListView.as_view(), name='doctor_appointments'),
    path('doctor/appointments/<int:pk>/update', DoctorUpdateAppointmentView.as_view(), name='appointment_update'),
    path('api/test/appointments/<int:pk>',UserAppointmentsView.as_view()),
]
