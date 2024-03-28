# views.py

import random
from datetime import datetime, timedelta

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializer import UserRegistrationSerializer
from rest_framework_simplejwt.views import TokenObtainPairView



class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('email')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user:
            # Generate a random token (this is for demonstration purposes only)
            token = random.randint(1, 10000)
            # Set token expiration to 1 day from now
            expires = datetime.now() + timedelta(days=1)

            return Response({
                'status': 'success',
                'access_token': token,
                'expires': expires
            })
        else:
            return Response({'status': 'error', 'message': 'Invalid credentials'}, status=401)


class UserJwtLoginApi(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # We are redefining post so we can change the response status on success
        # Mostly for consistency with the session-based API
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            response.status_code = status.HTTP_200_OK

        return response
