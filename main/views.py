# main/views.py
from django.views.generic import ListView, CreateView, View
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment
from .forms import AppointmentForm
from rest_framework.views import APIView
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Doctor
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.exceptions import NotAuthenticated
from rest_framework import status
from rest_framework.response import Response
from django.http import JsonResponse
from main.serializers import AppointmentSerializer,DoctorSerializer


class PatientAppointmentListView(APIView):
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect('login_view') 
        return super().handle_exception(exc)  

    def get(self,request,pk=None):
        apointments = Appointment.objects.filter(patient=request.user.patient)
        serializer = AppointmentSerializer(apointments,many=True)
        if request.headers['Accept'] == 'application/json':
            return JsonResponse(serializer.data,safe=False)
        return render(request,'appointments/patient_appointments.html',{"appointments":serializer.data})    


class AppointmentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        form = AppointmentForm()
        return render(request,'appointments/appointment.html',{"form":form})

    def post(self,request):
        form_data = {}
        form_files = None

        if request.content_type == 'application/json':
            form_data = request.data
            form = AppointmentForm(data=form_data,request=request)
        else:
            form_data = request.POST
            form = AppointmentForm(data=form_data,request=request)
        
        print("Is form valid?", form.is_valid()) 
        print(request.data)
        if form.is_valid():
            appointment = form.save()
            if request.headers['Accept'] == 'application/json':
                return Response(
                    {
                    "success":"appointment created",
                    "id":appointment.id
                    },
                    status=status.HTTP_201_CREATED
                    )
            return render(request,'appointments/partials/_appointment_result.html',{"form":form},status=status.HTTP_201_CREATED) 

        if request.headers['Accept'] == 'application/json':
            return JsonResponse(
                form.errors.get_json_data(),
                status=status.HTTP_400_BAD_REQUEST
            )
        return render(request,'appointments/partials/_appointment_result.html',{"form":form})    




class CancelAppointmentView( APIView):
    permission_classes = [IsAuthenticated] 
    def get(self,request,pk):
        appointment = get_object_or_404(Appointment, pk=pk)#, patient=request.user.patient)

        if appointment.status != 'cancelled':
            appointment.cancel()
        serializer = AppointmentSerializer(appointment)
        if request.headers.get('Accept') == 'application/json':
            return Response(
                {
                    "id":serializer.data.get('id'),
                    "status":serializer.data.get('status')
                }
                ,status=status.HTTP_200_OK
            )

        return render(request,'appointments/partials/_patient_appointment_row.html',{"appointment":serializer.data})


class filter_doctors_by_speciality(APIView):
    def get(self,request):
        speciality = request.GET.get('speciality')
        doctors = Doctor.objects.filter(speciality=speciality)

        if request.headers.get('Accept') == 'application/json':
            serializer = DoctorSerializer(doctors,many=True)
            return Response(serializer.data)
        html = render_to_string('appointments/partials/doctor_options.html', {'doctors': doctors})
        return HttpResponse(html)

class DoctorAppointmentListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        if request.user.role != 'doctor':
            return Response({"msg":"Not allowed for patients"},status=status.HTTP_403_FORBIDDEN)
        appointments = Appointment.objects.filter(doctor=request.user.doctor)

        if request.GET:
            print('get')
            reason = request.GET.get('reason')
            appointment_status = request.GET.get('status')
            if reason:
                apointments = appointments.filter(doctor=request.user.doctor,reason=reason)
            if appointment_status:
                print('status')
                appointments = appointments.filter(doctor=request.user.doctor,status=appointment_status)
                print(appointments)

        serializer = AppointmentSerializer(appointments,many=True)    
        print(serializer.data)
        if request.headers['Accept'] == 'application/json':
            return Response(serializer.data)
        if request.headers.get('HX-Request'):
            print('hx-here')
            return render(request,'appointments/partials/_appointments_table.html',{"appointments":serializer.data})  
            
        return render(request,'appointments/doctor_appointments.html',{"appointments":serializer.data})    

class DoctorUpdateAppointmentView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self,request,pk):
        if request.user.role != 'doctor':
            return Response(
                {"msg":"forbidden"},
                status=status.HTTP_403_FORBIDDEN
                )

        appointment = get_object_or_404(Appointment,pk=pk)
        if request.data:
            appointment_status = request.data.get('status')
            match appointment_status:
                case 'cancelled':
                    appointment.cancel()
                case 'confirmed':
                    appointment.confirm() 
                case 'completed':
                    appointment.mark_completed()
        serializer = AppointmentSerializer(appointment)          
        return render(request,'appointments/partials/_appointment_row.html',{"appointment":serializer.data}) 