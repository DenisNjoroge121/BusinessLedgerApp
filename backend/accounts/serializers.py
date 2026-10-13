from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Business, User

class AccountLocked(APIException):
    status_code = status.HTTP_423_LOCKED
    default_detail = "Too many failed attempts. Try again in 30 minutes."
    default_code = "account_locked"

class LockoutTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user =  User.objects.filter(username=attrs.get(self.username_fields)).first()
        if user and user.is_locked():
            raise AccountLocked()
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            if user:
                user.register_failed_attempt()
                user.refresh_from_db()
                if user.is_locked():
                    raise AccountLocked()
            raise
        self.user.reset.attempts()
        data["role"] = self.user.role
        data["business_id"] = self.user.business_id
        return data

class RegisterOwnerSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ["username", "password", "email", "phone_number", "business_name"]

    @transaction.atomic
    def create(self, validate_data):
        business = Business.objects.create(name=validated_data.pop("business_name"))
        return User.objects.create_user(business=business, role=User.Role.Owner, **validated_data)

class MeSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source="business.name", read_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number", "role", "business", "business_name"]
        