from rest_auth.registration.serializers import RegisterSerializer
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_auth.serializers import PasswordResetSerializer
from allauth.account.forms import ResetPasswordForm
from core.libs.errors import (
    invalid_email,
)
from core.libs.constants import auth_code

from .models import User, Profile, DriverLocation, OTP


# check if identity entered is email
def isEmail(identity):
    try:
        validate_email(identity)
        valid_email = True
    except ValidationError:
        valid_email = False
    return valid_email


class UserRegistrationSerializer(RegisterSerializer):
    """
    custom user registration serializer
    """

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    phonenumber = serializers.CharField(required=True)

    def get_cleaned_data(self):
        super(UserRegistrationSerializer, self).get_cleaned_data()
        number = self.validated_data.get("phonenumber", "")
        num_exists = User.objects.filter(phonenumber=number).exists()
        if num_exists:
            msg = {"phonenumber": ["A user with this phonenumber already exists"]}
            raise serializers.ValidationError(msg, code=auth_code)
        return {
            "first_name": self.validated_data.get("first_name", ""),
            "phonenumber": number,
            "last_name": self.validated_data.get("last_name", ""),
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password1", ""),
        }

    def save(self, request):
        user = super().save(request)
        number = self.cleaned_data.get("phonenumber")
        user.phonenumber = number
        user.save()
        return user


class DriverRegistrationSerializer(UserRegistrationSerializer):
    """
    driver registration serializer
    """

    def save(self, request):
        user = super().save(request)
        user.is_driver = True
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """
    enable login with phonenumber or email
    """

    email = serializers.CharField(max_length=300, required=True)
    password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        identity = attrs.get("email")
        password = attrs.get("password")

        if not identity and password:
            msg = "Must include email or phonenumber and password"
            raise serializers.ValidationError(msg, code="authorization")
        else:
            # check if email or phonenumber
            is_email = isEmail(identity)

            if is_email:
                usr = User.objects.filter(email=identity)
                if usr.exists():
                    # check if number is confirmed
                    usr_ = usr.first()
                    if not usr_.is_confirmed:
                        msg = "Please confirm your phonenumber first"
                        raise serializers.ValidationError(msg, code="authorization")

                    user = authenticate(
                        request=self.context.get("request"),
                        username=identity,
                        password=password,
                    )

                    if not user:
                        msg = "Could not login with credentials provided"
                        raise serializers.ValidationError(msg, code="authorization")
                else:
                    msg = "Email entered does not exist"
                    raise serializers.ValidationError(msg, code="authorization")
            else:
                raise serializers.ValidationError(invalid_email, code="authorization")
                # check if phonenumber exists
                usr = User.objects.filter(phonenumber=identity)
                if usr.exists():
                    usr_ = usr.first()

                    # check if confirmed
                    if not usr_.is_confirmed:
                        msg = "Please confirm your phonenumber first"
                        raise serializers.ValidationError(msg, code="authorization")

                    user = authenticate(
                        request=self.context.get("request"),
                        username=usr_.email,
                        password=password,
                    )
                    if not user:
                        msg = "Could not login with credentials provided"
                        raise serializers.ValidationError(msg, code="authorization")
                else:
                    msg = "Phonenumber entered does not exist"
                    raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs


# class LoginSerializer(serializers.Serializer):
#     """
#     enable login with  email
#     """

#     email = serializers.CharField(required=True)
#     password = serializers.CharField(required=True)

#     def validate(self, attrs):
#         identity = attrs.get("email")
#         password = attrs.get("password")

#         if not isEmail(identity):
#             raise serializers.ValidationError(email_not_existant, code=auth_code)
#         usr = User.objects.filter(email=identity)
#         if usr.exists():
#             if not usr.first().is_confirmed:
#                 raise serializers.ValidationError(unconfirmed_account, code=auth_code)

#             user = authenticate(
#                 request=self.context.get("request"),
#                 username=identity,
#                 password=password,
#             )

#             if not user:
#                 raise serializers.ValidationError(invalid_user, code=auth_code)
#         else:
#             raise serializers.ValidationError(email_not_existant, code=auth_code)

#         user_data = {
#             attribute: value
#             for attribute, value in vars(user).items()
#             if attribute != "_state"
#             and attribute != "password"
#             and attribute != "password"
#         }
#         return user_data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "image",
            "phonenumber",
            "is_admin",
            "is_driver",
            "is_superuser",
            "is_active",
            "partner",
            "date_joined",
            "is_confirmed",
        )


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["user"] = UserSerializer(read_only=True)
        return super(ProfileSerializer, self).to_representation(instance)


class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model = OTP
        fields = ("phonenumber", "otp")


class DriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverLocation
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["user"] = UserSerializer(read_only=True)
        return super(DriverLocationSerializer, self).to_representation(instance)


class PasswordSerializer(PasswordResetSerializer):
    password_reset_form_class = ResetPasswordForm
