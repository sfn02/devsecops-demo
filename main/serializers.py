from rest_framework import serializers
from main.models import Appointment
from users.models import (  
                            Doctor,
                            User,
                            Patient
                            )





class AppointmentSerializer(serializers.ModelSerializer):
    doctor = serializers.StringRelatedField()
    patient = serializers.StringRelatedField()
    date_scheduled = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    

    class Meta:
        model = Appointment
        fields = ['id', 'status', 'reason', 'patient','doctor','date_scheduled']


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['id','speciality']



class PatientAppointmentsSerializer(serializers.ModelSerializer):
    appointments = AppointmentSerializer(many=True)
    user = serializers.StringRelatedField()
    class Meta:
        model = Patient
        fields = ['user','appointments']

class DoctorAppointmentsSerializer(serializers.ModelSerializer):
    appointments = AppointmentSerializer(many=True)
    user = serializers.StringRelatedField()
    class Meta:
        model = Doctor
        fields = ['user','appointments']
