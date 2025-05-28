from django.urls import path
from .views import RegistrationFormView, ProfileView, LoginView,LogoutView,RefreshTokenView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    
    path('auth/register/',RegistrationFormView.as_view(),name='register_view'),
    path('auth/login/',LoginView.as_view(),name='login_view'),
    path('auth/logout/',LogoutView.as_view(),name='logout'),
    path('auth/token/refresh/',RefreshTokenView.as_view(),name='refresh_token_view'),
    path('profile/',ProfileView.as_view(),name='profile_view'),
    path('refresh/',RefreshTokenView.as_view())
    
]