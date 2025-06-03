from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Appointment, Doctor
from datetime import timedelta
class AppointmentForm(forms.ModelForm):
    speciality = forms.ChoiceField(
        choices=Doctor.SPECIALITY_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['reason', 'date_scheduled']
        widgets = {
            'date_scheduled': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                },
                format="%Y-%m-%d %H:%M"
            ),
            'reason': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'reason': 'Reason',
            'date_scheduled': 'Scheduled Date',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        

        if 'speciality' in self.data:
            try:
                speciality = self.data.get('speciality')
                self.fields['doctor'].queryset = Doctor.objects.filter(
                    speciality=speciality
                )
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        user = self.request.user
        doctor = self.cleaned_data.get('doctor')
        
        if not hasattr(user, 'patient'):
            return cleaned_data

        existing_appointments = Appointment.objects.filter(
            patient=user.patient,
            status='scheduled',
            date_scheduled__gt=timezone.now()
        ).exists()

        if existing_appointments:
            raise ValidationError(
                "Vous avez déjà un rendez-vous prévu à venir. "
                "Veuillez l'annuler avant d'en réserver un nouveau."
            )

      
        date_scheduled = cleaned_data.get('date_scheduled')
        if date_scheduled:
            if date_scheduled.hour < 7 or date_scheduled.hour >= 17:
                raise ValidationError({
                    'date_scheduled': 'Rendez-vous disponibles entre 7AM-5PM seulement'
                })
            if doctor:
           
                appointment_duration = timedelta(minutes=30) 
                start_time = date_scheduled
                end_time = date_scheduled + appointment_duration
                existing_appointments = Appointment.objects.filter(
                    doctor=doctor,
                    date_scheduled__lt=end_time, 
                    date_scheduled__gte=start_time - appointment_duration  
                )

                if self.instance and self.instance.pk:
                    existing_appointments = existing_appointments.exclude(pk=self.instance.pk)

                if existing_appointments.exists():
                    conflicting_appointment = existing_appointments.first()
                    raise ValidationError({
                        'date_scheduled': f'Le docteur a déjà un rendez-vous à {conflicting_appointment.date_scheduled.strftime("%H:%M")} le {conflicting_appointment.date_scheduled.strftime("%d/%m/%Y")}'
                    })

        return cleaned_data

    def clean_date_scheduled(self):
        date_scheduled = self.cleaned_data.get('date_scheduled')
        if date_scheduled and date_scheduled <= timezone.now():
            raise ValidationError(" La date prévue doit être dans le futur.")
        return date_scheduled

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.request and hasattr(self.request.user, 'patient'):
            instance.patient = self.request.user.patient
            
   
            doctor_id = self.request.data.get('doctor')
            if doctor_id:
                try:
                    instance.doctor = Doctor.objects.get(pk=doctor_id)
                except (Doctor.DoesNotExist, ValueError):
                    raise ValidationError({'doctor': 'Invalid doctor selected'})


            Appointment.objects.filter(
                patient=self.request.user.patient,
                status='scheduled',
                date_scheduled__lt=timezone.now()
            ).update(status='cancelled')

        if commit:
            instance.save()
        return instance