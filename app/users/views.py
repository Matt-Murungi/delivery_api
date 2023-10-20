from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate

from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from fcm_django.api.rest_framework import FCMDeviceSerializer
from fcm_django.models import FCMDevice

from .models import User, Profile, OTP, DriverLocation
from .serializers import (
    OTPSerializer,
    UserSerializer,
    ProfileSerializer,
    DriverRegistrationSerializer,
    DriverLocationSerializer,
)
from .utils import generate_otp


class ProfileApiView(GenericAPIView):
    """
    get and update user profile info
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        profile = Profile.objects.filter(user=user).first()
        profile_serializer = ProfileSerializer(profile)
        return Response(profile_serializer.data)

    def patch(self, request, format=None):
        id = request.data.get("id")
        profile = Profile.objects.filter(id=id).first()
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors)


class OPTApiView(GenericAPIView):
    """
    confirm or send otp
    """

    serializer_class = OTPSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # send otp
        user = request.user
        number = user.phonenumber
        otp = OTP.objects.filter(phonenumber=number, user=user).first()
        if not otp:
            otp = OTP.objects.create(phonenumber=number, user=user)
        otp_number = generate_otp()
        otp.send_otp(otp_number)
        data = {"OTP": ["An OPT code has been sent to your phone."]}
        return Response(data, status=status.HTTP_202_ACCEPTED)

    def post(self, request, *args, **kwargs):
        # check if otp is same
        user = request.user
        number = user.phonenumber
        otp = OTP.objects.filter(phonenumber=number, user=user).first()
        if not otp:
            data = {"OTP": ["Error, please request for your OTP code first."]}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("otp") == otp.otp:
            user.is_confirmed = True
            user.save()
            otp.is_validated = True
            otp.save()
            data = {"OTP": ["Account confirmed successfully."]}
            return Response(data, status.HTTP_202_ACCEPTED)
        else:
            data = {"OTP": ["Invalid OTP."]}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class DriverLocationApiView(GenericAPIView):
    """
    get, save and update driver location details
    """

    serializer_class = DriverLocationSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        location = DriverLocation.objects.filter(owner=user)[0]
        serializer = DriverLocationSerializer(location)
        return Response(data=serializer.data)

    def post(self, request, format=None, *args, **kwargs):
        serializer = DriverLocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors)

    def patch(self, request, format=None, *args, **kwargs):
        id = request.data.get("id")
        location = DriverLocation.objects.filter(id=id)
        serializer = DriverLocationSerializer(location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(serializer.errors)


class DriverRegistrationApi(GenericAPIView):
    """
    driver registration api
    """

    serializer_class = DriverRegistrationSerializer

    def post(self, request, format=None, *args, **kwargs):
        serializer = DriverRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            number = serializer.data["phonenumber"]
            token = Token.objects.filter(user__phonenumber=number).first()
            data = {"key": token.key}
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors)


class GetUsersApiView(GenericAPIView):
    """
    get all users except current user --- test api
    """

    permission_classes = [IsAuthenticated]

    serializer_class = UserSerializer

    def get(self, request):
        user = request.user
        users = User.objects.all().exclude(id=user.id)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class AccountDeletion(APIView):
    """
    confirm account deletion by verifying password,
    delete user account
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, format=None, *args, **kwargs):
        user = request.user
        usr = get_object_or_404(User, pk=user.id)
        if usr:
            usr.delete()
            msg = "Account deleted successfully"
            return Response(msg, status=status.HTTP_202_ACCEPTED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        user = request.user
        password = request.data.get("password")
        user = authenticate(request=request, username=user.username, password=password)
        if user:
            msg = "Password accepted"
            return Response(msg, status=status.HTTP_202_ACCEPTED)
        else:
            msg = "Incorrect password"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)


class FCMDeviceViewSet(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FCMDeviceSerializer

    def post(self, request, format=None):
        registration_id = request.data.get('registration_id')
        platform_type = request.data.get('type')
        if not registration_id:
            return Response({'error': 'registration_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        fcm_devices = FCMDevice.objects.filter(user=request.user)
        if fcm_devices.exists():
            fcm_device = fcm_devices.first()
            for device in fcm_devices[1:]:
                device.delete()
            if fcm_device.registration_id == registration_id:
                return Response({'message': 'Registration ID is already up to date'}, status=status.HTTP_200_OK)
            else:
                fcm_device.registration_id = registration_id
                fcm_device.type = platform_type
                fcm_device.save()
        else:
            fcm_device = FCMDevice(user=request.user, registration_id=registration_id, type=platform_type)
            fcm_device.save()

        serializer = FCMDeviceSerializer(fcm_device)
        return Response(serializer.data, status=status.HTTP_200_OK)