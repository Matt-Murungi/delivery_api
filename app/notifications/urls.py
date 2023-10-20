from django.urls import path

from .views import NotificationsApiView, DriverAvailabilityApiView

urlpatterns = [
    path("api/", NotificationsApiView.as_view()),
    path("api/driver/availability", DriverAvailabilityApiView.as_view())
]
