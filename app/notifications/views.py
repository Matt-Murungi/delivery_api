from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView

from core.libs.errors import (
    generate_error_for_not_existant,
    generate_internal_server_error,
)

from .models import Notification, OnlineDrivers
from .serializers import NotificationSerializer, DriverSerializer

User = get_user_model()


class NotificationsApiView(GenericAPIView):
    """
    get all notifications of a user
    """

    permission_classes = [IsAuthenticated]

    serializer_class = NotificationSerializer

    def get(self, request):
        user = request.user
        notifications = Notification.objects.filter(owner=user).order_by("-created_at")
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class DriverAvailabilityApiView(APIView):
    """
    Set Driver as available or not
    """

    permission_classes = [IsAuthenticated]
    serializer_class = DriverSerializer

    def get(self, request):
        user = request.user
        driver = OnlineDrivers.objects.filter(driver=user).first()
        print(driver)
        serializer = DriverSerializer(driver)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        try:
            user = request.user
            driver = User.objects.filter(email=user).first()
            if not driver or driver.is_driver is False:
                return Response(
                    generate_error_for_not_existant("Driver"),
                    status=status.HTTP_404_NOT_FOUND,
                )
            online_driver = OnlineDrivers.objects.filter(driver=driver).first()
            if not online_driver:
                OnlineDrivers.objects.create(driver=driver)
            online_driver.latitude = request.data["latitude"]
            online_driver.longitude = request.data["longitude"]
            online_driver.is_active = request.data["is_active"]
            serializer = DriverSerializer(online_driver)
            online_driver.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                data=generate_internal_server_error,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
