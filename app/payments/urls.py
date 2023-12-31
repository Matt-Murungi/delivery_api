from django.urls import path

from .views import (
    OrderApiView,
    GetOrdersApiView,
    ConfirmOrderPaymentApiView,
    GetOrderAmountApiView,
    GetOrderApiView,
    AcceptOrderApiView,
    OwnerOrdersApiView,
    UpdateOrderStatusApiView,
    DriverGetOrdersApiView,
    EarningsApiView,
    PaymentApiView,
    make_payment_request,
    CashPaymentApiView,
    GetPaymentApiview,
    GetDriverApiView,
    DriverBankingInformationApiView,
    UpdateDriverBankingInformationApiView,
    RequestEarningsApiView,
    DriverCancelOrderApiView,
    UserCancelOrderApiView,
    DriverOrdersApiView,
    DriverPaymentApiView,
    OngoingOrderApiView,
)

urlpatterns = [
    path("api/order/", OrderApiView.as_view()),
    path("api/order/ongoing/", OngoingOrderApiView.as_view()),
    path("api/orders/all/", GetOrdersApiView.as_view()),
    path("api/get/order/<int:id>/", GetOrderApiView.as_view()),
    path(
        "api/get/order/payment/confirm/<int:id>/", ConfirmOrderPaymentApiView.as_view()
    ),
    path("api/order/get/amount/<int:id>/", GetOrderAmountApiView.as_view()),
    path("api/get/driver/<int:id>/", GetDriverApiView.as_view()),
    path("api/driver/accept/", AcceptOrderApiView.as_view()),
    path("api/owner/", OwnerOrdersApiView.as_view()),
    path("api/update/", UpdateOrderStatusApiView.as_view()),
    path("api/driver/orders/", DriverGetOrdersApiView.as_view()),
    path("api/earnings/", EarningsApiView.as_view()),
    path("api/payments/", PaymentApiView.as_view()),
    path("api/payments/make/", make_payment_request),
    path("api/payments/cash/make/", CashPaymentApiView.as_view()),
    path("api/payment/<int:id>/", GetPaymentApiview.as_view()),
    path("api/get/driver/<int:id>/", GetDriverApiView.as_view()),
    path("api/driver/banking/information/", DriverBankingInformationApiView.as_view()),
    path(
        "api/driver/banking/information/update/<int:id>/",
        UpdateDriverBankingInformationApiView.as_view(),
    ),
    path("api/driver/request/earning/", RequestEarningsApiView.as_view()),
    path("api/driver/cancel/", DriverCancelOrderApiView.as_view()),
    path("api/owner/order/cancel/", UserCancelOrderApiView.as_view()),
    path("api/driver/orders/all/", DriverOrdersApiView.as_view()),
    path("api/driver/orders/payment/status/<int:id>/", DriverPaymentApiView.as_view()),
]
