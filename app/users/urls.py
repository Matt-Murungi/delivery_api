from django.urls import path
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet



from .views import (
    AccountDeletion,
    ProfileApiView,
    DriverRegistrationApi,
    OPTApiView,
    DriverLocationApiView,
    GetUsersApiView,
    FCMDeviceViewSet
)

urlpatterns = [
    path("api/user/profile/", ProfileApiView.as_view()),
    path("api/user/confirm/", OPTApiView.as_view()),
    # path("api/user/driver/registration/", DriverRegistrationApi.as_view()),
    path("api/user/delete/", AccountDeletion.as_view()),
    path("api/driver/location/", DriverLocationApiView.as_view()),
    path("api/get/", GetUsersApiView.as_view()),
    path(
        "api/devices/",
        FCMDeviceViewSet.as_view(),
        # FCMDeviceAuthorizedViewSet.as_view({"post": "create"}),
        name="create_fcm_device",
    ),
]
