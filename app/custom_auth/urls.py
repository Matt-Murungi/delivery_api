from django.urls import path

from .views import (
    UserRegistrationApiView,
    DriverRegistrationApiView,
    RequestOTPApiView,
    OTPConfirmApiView,
)

urlpatterns = [
    path("user/registration/", UserRegistrationApiView.as_view(), name="user_registration"),
    path("driver/registration/", DriverRegistrationApiView.as_view()),
    path("request/otp/", RequestOTPApiView.as_view()),
    path("confirm/otp/", OTPConfirmApiView.as_view(), name="otp_confirm"),
]
