from django.test import TestCase

# Create your tests here.
from django.urls import path

from .views import LoginView, UserRegistrationView, UserJwtLoginApi
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', UserJwtLoginApi.as_view()),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
]
