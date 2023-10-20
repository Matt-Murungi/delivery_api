from django.contrib.auth import get_user_model

from rest_framework.validators import UniqueValidator
from rest_framework import serializers

from .models import CustomOTP, PreassignedOTP

User = get_user_model()


class CustomUserRegistrationSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phonenumber = serializers.CharField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="Phonenumber already exists",
            )
        ],
    )
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all(), message="Email already exists")
        ],
    )


class CustomLoginSerializer(serializers.Serializer):
    phonenumber = serializers.CharField(required=True)

    def validate_phonenumber(self, value):
        number_exists = User.objects.filter(phonenumber=value).exists()
        if not number_exists:
            msg = "User with phonenumber entered does not exist"
            raise serializers.ValidationError(msg)
        return value


class ConfirmOTPSerializer(serializers.Serializer):
    phonenumber = serializers.CharField(required=True)
    otp = serializers.CharField(required=True)

    def validate_phonenumber(self, value):
        number_exists = User.objects.filter(phonenumber=value).exists()
        if not number_exists:
            msg = "User with phonenumber entered does not exist"
            return serializers.ValidationError(msg)
        return value

    def validate_otp(self, value):
        otp_exists = CustomOTP.objects.filter(otp=value)

        if not otp_exists:
            preassigned_otp = PreassignedOTP.objects.filter(otp=value)
            if not preassigned_otp:
                msg = "OTP value entered does not exist"
                return serializers.ValidationError(msg)
            otp_exists = preassigned_otp
        return value

