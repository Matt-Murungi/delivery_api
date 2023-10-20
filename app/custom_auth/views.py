from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth import login

from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from rest_framework import status

from .serializers import (
    CustomUserRegistrationSerializer,
    CustomLoginSerializer,
    ConfirmOTPSerializer,
)
from .models import CustomOTP, PreassignedOTP
from .utils import generate_otp

from users.serializers import UserSerializer

User = get_user_model()


class UserRegistrationApiView(GenericAPIView):
    """
    registers user account, requires email, phonenumber,
    first_name and last_name
    """

    serializer_class = CustomUserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = CustomUserRegistrationSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                data = request.data
                email = data.get("email")
                number = data.get("phonenumber")
                first_name = data.get("first_name")
                last_name = data.get("last_name")
                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    phonenumber=number,
                )
                user.set_unusable_password()
                user.save()

                serializer = UserSerializer(user)

                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"detail": f"Internal Server Error {e.detail}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DriverRegistrationApiView(GenericAPIView):
    """
    registers driver account, requires email, phonenumber,
    first_name and last_name
    """

    serializer_class = CustomUserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = CustomUserRegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = request.data
            email = data.get("email")
            number = data.get("phonenumber")
            first_name = data.get("first_name")
            last_name = data.get("last_name")
            user = User(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phonenumber=number,
            )
            user.is_driver = True
            user.set_unusable_password()
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestOTPApiView(GenericAPIView):
    """
    takes user phonenumber and sends OTP code
    """

    serializer_class = CustomLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = CustomLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = request.data
            number = data.get("phonenumber")
            user = User.objects.filter(phonenumber=number).first()
            if user:
                otp = generate_otp()
                custom_otp, is_created = CustomOTP.objects.get_or_create(
                    user=user, phonenumber=number
                )
                custom_otp.send_otp(otp)
                msg = {"detail": "An OTP code has been sent to your phonenumber."}
                return Response(msg)
            else:
                msg = {"detail": "User does not exist, something went wrong"}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        else:
            Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OTPConfirmApiView(GenericAPIView):
    """
    takes phonenumber and OTP code and confirms OTP
    validity, requires phonumber and OTP code
    """

    serializer_class = ConfirmOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = ConfirmOTPSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = request.data
            number = data.get("phonenumber")
            otp = data.get("otp")
            user = User.objects.filter(phonenumber=number).first()
            if not user:
                msg = {"detail": "No user with such phonenumber"}
                return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)
            custom_otp = CustomOTP.objects.filter(otp=otp).first()
            if not custom_otp:
                preassigned_otp = PreassignedOTP.objects.filter(otp=otp).first()
                if not preassigned_otp:
                    msg = {"detail": "No otp with such value"}
                    return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)
                custom_otp = preassigned_otp
            if custom_otp.user != user:
                msg = {"detail": "OTP number provided is incorrect"}
                return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)
            if not user.is_confirmed:
                user.is_confirmed = True
                user.save()
            if not custom_otp.is_validated:
                custom_otp.is_validated = True
                custom_otp.save()
            auth = authenticate(request, phonenumber=user.phonenumber)
            login(request, user=auth)
            token = Token.objects.filter(user__phonenumber=number).first()
            data = {"detail": "OTP code successfully confirmed", "key": token.key}
            return Response(data=data, status=status.HTTP_200_OK)
        else:
            Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
