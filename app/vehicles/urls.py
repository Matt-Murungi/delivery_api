from django.urls import path

from .views import (
    VehicleApiView,
    VehicleOwnerApiView,
    GetVehicleApiView,
    GetDriverVehiclesApiView,
    DeleteVehicleApiView,
)

urlpatterns = [
    path("api/", VehicleApiView.as_view()),
    path("api/<int:id>/", GetVehicleApiView.as_view()),
    path("api/driver/<int:id>/", GetDriverVehiclesApiView.as_view()),
    path("api/delete/vehicle/", DeleteVehicleApiView.as_view()),
    path("api/owner/", VehicleOwnerApiView.as_view()),
]
