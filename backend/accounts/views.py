from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import (LockoutTokenObtainPairSerializer,MeSerializer,                          RegisterOwnerSerializer)

# Create your views here.


class LoginView(TokenObtainPairView):
    serializer_class = LockoutTokenObtainPairSerializer


class RegisterOwnerView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterOwnerSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveAPIView):
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user