from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.views.static import serve


schema_view = get_schema_view(
    openapi.Info(
        title="bdeliv API",
        default_version="v1",
        # description="Test description",
        # terms_of_service="https://www.ourapp.com/policies/terms/",
        # contact=openapi.Contact(email="bdeliv@bdeliv.com"),
        # license=openapi.License(name="Test License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", include("admin_honeypot.urls", namespace="admin_honeypot")),
    path("site/admin/sdfe/", admin.site.urls),
    path("auth/", include("rest_auth.urls")),
    path("auth/", include("allauth.urls")),
    path("auth/registration/", include("rest_auth.registration.urls")),
    path("custom/auth/", include("custom_auth.urls")),
    path("users/", include("users.urls")),
    path("admins/", include("admins.urls")),
    path("vehicles/", include("vehicles.urls")),
    path("partners/", include("partners.urls")),
    path("bookings/", include("bookings.urls")),
    path("payments/", include("payments.urls")),
    path("notifications/", include("notifications.urls")),
    path("feedback/", include("feedback.urls")),
    path("", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path(
        "docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(
        "api/api.json/",
        schema_view.without_ui(cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.STATIC_ROOT}),
]


urlpatterns = urlpatterns + static(
    settings.STATIC_URL,
)
urlpatterns = urlpatterns + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)
