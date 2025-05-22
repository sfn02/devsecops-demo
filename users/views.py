from django.views import View
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate,get_user_model,logout
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PatientRegistrationSerializer, ProfileSerializer,UserSerializer, CustomTokenObtainPairSerializer
from .models import User
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated
from .forms import RegisterForm, AppointmentForm
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime,timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json


class RegistrationFormView(APIView):
    def get(self,request):
        form = RegisterForm()
        context = {"form":form}
        return render(request,'users/register.html',context)

    def post(self,request):
        print(request.data)
        if request.content_type == 'application/json':
            form = RegisterForm(request.data)
            print(form.is_valid())
            if form.is_valid():
                user = form.save()
                response = Response({
                    "msg":"User created",
                    "user":{
                        "user_id":user.id,
                        "email":user.email
                    }
                }
                    ,status=status.HTTP_201_CREATED)   
                return response
            errors = [
                    form.errors.get_json_data()  
            ]   
            return Response(errors,status=status.HTTP_400_BAD_REQUEST)
        
        form = RegisterForm(request.POST)

        print(form.is_valid())
        print(request.content_type)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=status.HTTP_201_CREATED)
            if request.headers.get('HX-Request') == 'true':
                response['HX-Redirect'] = reverse('login_view')   
            return response
        else:
            return render(request, 'users/register.html', {'form': form})
              
    
     

'''class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,pk):
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request,pk):
        user = User.objects.get(pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({"err":serializer.errors})  '''






class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def handle_exception(self, exc):
        if isinstance(exc, NotAuthenticated):
            return redirect('login_view') 
        return super().handle_exception(exc)  
    def get(self, request,pk=None):
        user = get_user_model()
        if pk:
            print(pk)
            user = user.objects.get(pk=pk)
        else:    
            user = request.user    

        serializer = UserSerializer(user)   
         
        if request.headers['Accept'] == 'application/json':
            return JsonResponse(serializer.data)

        return render(request, 'users/profile.html', {'user': request.user})

    def post(self, request):
        user = get_user_model()
        user_id = request.data.get('user_id',request.user.id)
        print(user_id)
        user = user.objects.filter(id=user_id).first()
        user.email = request.data.get('email', user.email)
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name',user.last_name)
        password = request.data.get('password')
        if password:
            user.set_password(
                password
            )
        user.save()
        if request.headers.get('Accept') == 'application/json':
            response = Response({"msg":"Profile updated succesfully"},status=status.HTTP_201_CREATED)
        else:
            response = Response("<small>Profile updated successfully</small>",status=status.HTTP_201_CREATED)
        return response






class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    def post(self,request,*args,**kwargs):
        response_from_jwt = super().post(request,*args,**kwargs)

        if response_from_jwt.status_code == status.HTTP_200_OK:
            data = response_from_jwt.data
            refresh = data.get('refresh')
            access = data.get('access')

            response = Response(
                {
                    "msg":"Login succesfull",
                    "refresh":refresh,
                    "access":access
                }
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh,
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            response.set_cookie(
                key='access_token',
                value=access,
                httponly=True,
                secure=False,
                samesite='Lax'
            )
            if request.headers.get('HX-Request') == 'true':
                response['HX-Redirect'] = reverse('profile_view')
            return response
        return HttpResponse("<small>Invalid credentials</small>",status=status.HTTP_401_UNAUTHORIZED)
    def get(self,request):
        return render(request,template_name='users/login.html')

class RefreshToken(TokenRefreshView):
    serializer_class = TokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        print(1)
        response = redirect('login_view')
        refresh = request.COOKIES.get('refresh')
        if refresh:
            token = RefreshToken(refresh)
            print(2)
            token.blacklist()
            print("token blacklisted")
        
        response.delete_cookie(
            key='access_token',
            path='/',
            )
        response.delete_cookie(
            key='refresh_token',
            path='/',
            )

        logout(request)
        return response