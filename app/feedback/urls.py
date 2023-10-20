from django.urls import path

from .views import *

urlpatterns = [
    path("api/driver/ratings/", DriverRatingsApiView.as_view()),
    path("api/driver/avg/rating/", DriverAverageRatingsApiView.as_view()),
    path("api/get/rating/<int:id>/", GetRatingApiView.as_view()),
    path("api/owner/ratings/", OwnerRatingsApiView.as_view()),
]
