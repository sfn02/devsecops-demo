from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import Doctor, Patient

class Appointment(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Prévu'),
        ('confirmed', 'Confirmé'),
        ('cancelled', 'Annulé'),
        ('completed', 'Terminé'),

    ]
    REASON_CHOICES = [
        ('consultation','Consultation'),
        ('suivi','Suivi'),
        ('autre','Autre')
    ]

    patient = models.ForeignKey(
        Patient,
        related_name = 'appointments',
        limit_choices_to={'role':'patient'},
        on_delete=models.CASCADE 
    )  
    doctor = models.ForeignKey(
        Doctor,
        related_name='appointments',
        limit_choices_to={'role':'doctor'},
        on_delete=models.CASCADE
    )
    reason = models.TextField(choices=REASON_CHOICES,null=False,blank=False)
    status = models.CharField(max_length=10,choices=STATUS_CHOICES,default='scheduled')
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    date_scheduled = models.DateTimeField(null=False,blank=False)

    def cancel(self):
        self.status = 'cancelled'
        self.save()

    def confirm(self):
        self.status = 'confirmed'
        self.save()

    def complete(self):
        self.status = 'completed'
        self.save()






    def __str__(self):
        return f"Appointment for {self.patient} with {self.doctor} at {self.date_created}"

# Create your models here.
