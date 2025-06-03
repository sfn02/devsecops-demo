from django.urls import path
from .views import  ProfileView, LoginView,LogoutView,RefreshTokenView, RegisterView


urlpatterns = [
    

    path('auth/register/',RegisterView.as_view(),name='register_view'),
    path('auth/login/',LoginView.as_view(),name='login_view'),
    path('auth/logout/',LogoutView.as_view(),name='logout'),
    path('auth/token/refresh/',RefreshTokenView.as_view(),name='refresh_token_view'),
    path('profile/',ProfileView.as_view(),name='profile_view'),
   
]