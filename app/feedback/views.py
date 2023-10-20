from django.db.models import Avg

from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import DriverRatingsSerializer
from .models import DriverRating


class DriverRatingsApiView(GenericAPIView):
    """
    creates and lists all ratings, requires driver id,
    owner id, both driver and owner are user accounts finally
    ratings a positive integer between 1 and 5. Updates previuosly made
    rating by user if already exists.
    """

    serializer_class = DriverRatingsSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        ratings = DriverRating.objects.all()
        serializer = DriverRatingsSerializer(ratings, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = DriverRatingsSerializer(data=request.data)
        if serializer.is_valid():
            data = request.data
            rating = DriverRating.objects.filter(
                owner__id=data["owner"], driver__id=data["driver"]
            )
            if rating.exists():
                rating_ = rating.first()
                rating_.ratings = data["ratings"]
                rating_.save()
                serializer = DriverRatingsSerializer(rating_)
                return Response(serializer.data)
            else:
                serializer.save()
                return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetRatingApiView(GenericAPIView):
    """
    get a specific rating, update a specific rating and
    deletes a rating, requires rating id
    """

    serializer_class = DriverRatingsSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        rating = DriverRating.objects.filter(id=id).first()
        if rating is not None:
            serializer = DriverRatingsSerializer(rating)
            return Response(serializer.data)
        msg = {"detail": f"No rating with id {id}"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, id, *args, **kwargs):
        id = request.data.get("id")
        if not id:
            msg = {"detail": "id is required for this operation"}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        rating = DriverRating.objects.filter(id=id).first()
        if rating is not None:
            serializer = DriverRatingsSerializer(
                rating, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors)

        msg = {"detail": f"No rating with id {id}"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, *args, **kwargs):
        id = request.data.get("id")
        if not id:
            msg = {"detail": "id is required for this operation"}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        rating = DriverRating.objects.filter(id=id).first()
        if rating is not None:
            rating.delete()
            msg = {"detail": "rating succesfully deleted"}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        msg = {"detail": f"No rating with id {id}"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)


class DriverAverageRatingsApiView(GenericAPIView):
    """
    returns a drivers average ratings and ratings count
    """

    serializer_class = DriverRatingsSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = 0
        avg = 0
        user = request.user
        ratings = DriverRating.objects.filter(driver=user)
        count_ = ratings.count()
        if count_ > 0:
            count = count_
            avg = ratings.aggregate(Avg("ratings"))
        data = {"count": count, "average": avg}
        return Response(data)


class OwnerRatingsApiView(GenericAPIView):
    """
    returns all ratings a user has made
    """

    serializer_class = DriverRatingsSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        ratings = DriverRating.objects.filter(owner=user)
        serializer = DriverRatingsSerializer(ratings, many=True)
        return Response(serializer.data)
