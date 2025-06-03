from django.views import View
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate,get_user_model,logout
from django.contrib.auth.password_validation import validate_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.serializers import  UserSerializer, CustomTokenObtainPairSerializer
from users.models import User
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import NotAuthenticated
from users.forms import RegisterForm
from rest_framework_simplejwt.exceptions import TokenError,InvalidToken
   
     
class RegisterView(APIView):

    def get(self,request):
        form = RegisterForm()
        context = {"form":form}
        return render(request,'users/register.html',context)

    def post(self, request):
        print(request.data)
        
       
        if request.content_type == 'application/json':
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    "msg": "User created",
                    "user": {
                        "user_id": user.id,
                        "email": user.email
                    }
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        serializer = UserSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.save()
            return redirect('login_view')
        else:
        
            return render(request, 'users/register.html', {
                'form': serializer,
                'serializer_errors': serializer.errors
            })

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

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        if request.headers.get('Accept') == 'application/json':
            return Response(serializer.data)
        return render(request,'users/profile.html',{"user":serializer.data})

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if request.headers.get('Accept') == 'application/json':
                return Response(
                    {
                        "success":"Profile updated succesfully"
                    }
                )
            return render(request,'users/partials/_success.html',{"user":serializer.data})
        else:
            if request.headers.get('Accept') == 'application/json':
                return Response(serializer.errors)
            return render(request, 'users/partials/_errors.html', {'serializer': serializer}) 

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

class root_redirect(APIView):
    def get(self,request):
        if request.user.is_authenticated:
            return redirect('profile_view')
        else:
            return redirect('login_view')    

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



