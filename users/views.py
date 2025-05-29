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
from rest_framework_simplejwt.exceptions import TokenError,InvalidToken


class RegistrationFormView(APIView):
    def get(self,request):
        form = RegisterForm()
        context = {"form":form}
        return render(request,'users/register.html',context)

    def post(self,request):
        print(request.data)
        if request.content_type == 'application/json':
            form = RegisterForm(request.data)
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
        if form.is_valid():
            form.save()
            response = redirect('login_view')   
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
    def get(self, request):
        user = get_user_model()
        user = request.user    
        serializer = UserSerializer(user)   
         
        if request.headers['Accept'] == 'application/json':
            return JsonResponse(serializer.data)
        return render(request, 'users/profile.html', {'user': request.user})

    def put(self, request):
        user = get_user_model()
        user = user.objects.get(pk=request.user.id)
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
            response = Response({"success":"Profile updated succesfully"},status=status.HTTP_201_CREATED)
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
                ,
                status=status.HTTP_200_OK
                )
            response['Location'] = reverse('profile_view')
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

class RefreshTokenView(TokenRefreshView):
    def post(self,request):
        refresh = request.COOKIES.get('refresh_token') or request.data.get('refresh')
        if refresh:
            try:
                old_refresh = RefreshToken(refresh)
                old_refresh.blacklist()
                new_refresh = RefreshToken()
                access = str(new_refresh.access_token)
                refresh = str(new_refresh)
                old_refresh.blacklist()
                response = Response(
                    {
                    "access":access,
                    "refresh":refresh
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
                return response
            except (TokenError,InvalidToken) as e:
                return Response(
                    {
                        "error":str(e)
                    }
                )




class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        response = redirect('login_view')
        
        refresh = request.COOKIES.get('refresh_token') or request.data.get('refresh')
        if refresh:
            token = RefreshToken(refresh)
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

def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('profile_view')
    else:
        return redirect('login_view')    