from django.urls import path

from .views import (
    BookingsAllApiView,
    GetUserBookingsApi,
    ConfirmBookingApiView,
    BookingsApiView,
    GetBookingApiView,
    DeleteBookingApiView,
    ReceiverApiView,
    GetBookingReceiverApiView,
    DeleteReceiverApiView,
    ProductsApiView,
    GetBookingProductApiView,
    DeleteProductApiView,
    GetAmountRange,
    ConfirmBookingReceiveApiView,
)

urlpatterns = [
    path("api/all/", BookingsAllApiView.as_view()),
    path("api/get/", GetUserBookingsApi.as_view()),
    path("api/confirm/<int:id>/", ConfirmBookingApiView.as_view()),
    path("api/bookings/", BookingsApiView.as_view(), name="booking"),
    path("api/booking/<int:id>/", GetBookingApiView.as_view()),
    path("api/delete/booking/", DeleteBookingApiView.as_view()),
    path("api/receiver/", ReceiverApiView.as_view()),
    path("api/receiver/<int:id>/", GetBookingReceiverApiView.as_view()),
    path("api/delete/receiver/", DeleteReceiverApiView.as_view()),
    path("api/products/", ProductsApiView.as_view()),
    path("api/products/<int:id>/", GetBookingProductApiView.as_view()),
    path("api/delete/product/", DeleteProductApiView.as_view()),
    path("api/booking/amount/range/<int:id>/", GetAmountRange.as_view()),
    path("api/booking/confirm/", ConfirmBookingReceiveApiView.as_view()),
]
