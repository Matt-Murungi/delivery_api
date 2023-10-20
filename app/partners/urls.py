from django.urls import path


from .views import (
    PartnerView,
    PartnerOwnerApiView,
    GetPatnerApiView,
    PartnerAuthenticationView,
    PartnerProductApiView,
    AllPartnerProductApiView,
    PartnerProductGetApiView,
    ProductCategoryApiView,
    CustomerProductAPIView,
    PartnerOrderAPIView,
    PartnerOrderStatusApiView,
    PartnerOrdersStatusApiView,
    PartnerPaymentsApiView

)


urlpatterns = [
    path("api/", PartnerView.as_view()),
    path("api/<int:id>/", GetPatnerApiView.as_view()),
    path("api/owner/", PartnerOwnerApiView.as_view()),
    path(
        "api/auth", PartnerAuthenticationView.as_view(), name="partner-authentication"
    ),
    path("api/product/", PartnerProductApiView.as_view()),
    path("api/product/<int:id>/", PartnerProductGetApiView.as_view()),
    path("api/products/all/", AllPartnerProductApiView().as_view()),
    path("api/products/category", ProductCategoryApiView().as_view()),
    path("api/product/customer", CustomerProductAPIView().as_view()),
    path("api/order/<int:id>/", PartnerOrderAPIView().as_view()),
    path("api/order/status", PartnerOrdersStatusApiView().as_view()),
    path("api/order/status/<int:id>/", PartnerOrderStatusApiView().as_view()),
    path("api/payments/", PartnerPaymentsApiView().as_view()),
]
