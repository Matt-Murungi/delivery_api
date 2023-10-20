from django.db.models import Avg

from django.contrib.auth.models import User as AdminUser
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from users.models import User, Profile
from users.serializers import UserSerializer, ProfileSerializer
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer

from payments.models import (
    Order,
    Earnings,
    Payment,
    RequestEarnings,
    DriverBankingInformation,
)
from payments.serializers import (
    OrderSerializer,
    EarningsSerializer,
    PaymentSerializer,
    RequestEarningsSerializer,
    DriverBankingInformation,
    DriverBankingInformationSerializer,
)
from bookings.models import Bookings
from bookings.serializers import BookingSerializer
from feedback.models import DriverRating
from feedback.serializers import DriverRatingsSerializer


class DriverRatingsApiView(ListAPIView):
    """
    perfom any rating related query
    """

    permission_classes = [IsAdminUser]
    serializer_class = DriverRatingsSerializer
    queryset = DriverRating.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "id",
        "owner__id",
        "owner__first_name",
        "owner__last_name",
        "driver__id",
        "driver__first_name",
        "driver__last_name",
        "ratings",
        "created_at",
    )


class DriverRatingsRanking(GenericAPIView):
    """
    returns drivers based on their average ratings
    """

    permission_classes = [IsAdminUser]

    serializer_class = DriverRatingsSerializer

    def get(self, request, *args, **kwargs):
        ratings = (
            DriverRating.objects.values(
                "driver", "driver__first_name", "driver__last_name"
            )
            .annotate(ratings_avg=Avg("ratings"))
            .order_by("-ratings_avg")
        )
        return Response(ratings)


class UsersApiView(ListAPIView):
    """
    perform any user related query
    """

    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "email",
        "id",
        "first_name",
        "last_name",
        "phonenumber",
        "is_admin",
        "is_driver",
        "date_joined",
        "is_superuser",
    )


class UserUpdateApiView(GenericAPIView):
    """
    perform update on user, requres user id
    """

    permission_classes = [IsAdminUser]

    serializer_class = UserSerializer

    def patch(self, request, *args, **kwargs):
        user_id = request.data.get("id")
        user = User.objects.filter(id=user_id).first()
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class UserDeleteApiView(GenericAPIView):
    """
    deletes a user account, requires id
    """

    permission_classes = [IsAdminUser]

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        id = request.data.get("id")
        if not id:
            msg = {"details": "id is required for this operation"}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=id).first()
        if user is not None:
            user.delete()
            msg = {"details": f"user account with id {id} deleted succesfully"}
            return Response(msg)

        msg = {"details": f"no user exists with id {id}"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserPassword(GenericAPIView):
    """
    perform update on user password, requires user id
    """

    permission_classes = [IsAdminUser]

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("id")
        user = AdminUser.objects.filter(id=user_id).first()

        if not user:
            msg = "User id does not exist"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get("password")
        if not password:
            msg = "Password is required"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(password)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class ProfileApiView(ListAPIView):
    """
    perform any profile related query
    """

    permission_classes = [IsAdminUser]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "id",
        "user",
        "user__id",
        "user__is_driver",
        "user__email",
        "user__phonenumber",
        "is_approved",
    )


class ProfileUpdateApiView(GenericAPIView):
    """
    perform update on profile, requires profile id
    """

    permission_classes = [IsAdminUser]

    serializer_class = ProfileSerializer

    def patch(self, request, *args, **kwargs):
        profile_id = request.data.get("id")
        profile = Profile.objects.filter(id=profile_id).first()
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class VehicleApiView(ListAPIView):
    """
    perform any vehicle related query
    """

    permission_classes = [IsAdminUser]
    serializer_class = VehicleSerializer
    queryset = Vehicle.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "owner__id",
        "owner__phonenumber",
        "id",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "reg_number",
        "vehicle_type",
        "color",
        "insurance_expiry",
        "model",
    )


class VehicleUpdateApiView(GenericAPIView):
    """
    perform update on vehicle, requires vehicle id
    """

    permission_classes = [IsAdminUser]

    serializer_class = VehicleSerializer

    def patch(self, request, *args, **kwargs):
        vehicle_id = request.data.get("id")
        vehicle = Vehicle.objects.filter(id=vehicle_id).first()
        serializer = VehicleSerializer(vehicle, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class OrderApiView(ListAPIView):
    """
    perform any order related query
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "owner__id",
        "owner__phonenumber",
        "id",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "booking__id",
        "booking__booking_id",
        "amount",
        "status",
        "created_at",
        "driver__id",
        "driver__phonenumber",
        "driver__email",
        "driver__first_name",
        "driver__last_name",
        "booking__booking_receiver__name",
        "booking__booking_receiver__phonenumber",
        "booking__booking_product__product_type",
    )


class OrderUpdateApiView(GenericAPIView):
    """
    perform update on order, requires order id
    """

    permission_classes = [IsAdminUser]

    serializer_class = OrderSerializer

    def patch(self, request, *args, **kwargs):
        order_id = request.data.get("id")
        order = Order.objects.filter(id=order_id).first()
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class EarningsApiView(ListAPIView):
    """
    perform any order related query
    """

    permission_classes = [IsAdminUser]
    serializer_class = EarningsSerializer
    queryset = Earnings.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "owner__id",
        "owner__phonenumber",
        "id",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "amount",
        "created_at",
    )


class EarningsUpdateApiView(GenericAPIView):
    """
    update earnings, requires id
    """

    permission_classes = [IsAdminUser]

    serializer_class = EarningsSerializer

    def patch(self, request, *args, **kwargs):
        id = request.data.get("id")
        earning = Earnings.objects.filter(id=id).first()
        serializer = EarningsSerializer(earning, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class PaymentApiView(ListAPIView):
    """
    perform any payment related query
    """

    permission_classes = [IsAdminUser]
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "owner__id",
        "owner__phonenumber",
        "id",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "amount",
        "created_at",
        "transaction_id",
        "status",
        "card_code",
    )


class PaymentUpdateApiView(GenericAPIView):
    """
    perform update on payment, requires payment id
    """

    permission_classes = [IsAdminUser]

    serializer_class = PaymentSerializer

    def patch(self, request, *args, **kwargs):
        payment_id = request.data.get("id")
        payment = Payment.objects.filter(id=payment_id).first()
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class MakePaymentRefundApiview(GenericAPIView):
    """
    make transaction refund, requires amount, last four credit card numbers
    and transaction id
    """

    pass


class GetEarningsRequestApiView(ListAPIView):
    """
    perform any earnings request query
    """

    permission_classes = [IsAdminUser]
    serializer_class = RequestEarningsSerializer
    queryset = RequestEarnings.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "owner__id",
        "owner__phonenumber",
        "id",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "amount",
        "created_at",
    )


class EarningsRequestApiView(GenericAPIView):
    """
    update earning request, requires earning request id
    """

    permission_classes = [IsAdminUser]

    serializer_class = RequestEarningsSerializer

    def patch(self, request, id, *args, **kwargs):
        if id is not None:
            earning_request = RequestEarnings.objects.filter(id=id).first()
            if earning_request is not None:
                serializer = RequestEarningsSerializer(
                    earning_request, data=request.data, partial=True
                )
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response(serializer.errors)
            msg = f"Earning Request with id {id} does not exist"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        else:
            msg = "Please provide an Earning Request id"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)


class BookingsApiView(ListAPIView):
    """
    perform any bookings related query
    """

    permission_classes = [IsAdminUser]
    serializer_class = BookingSerializer
    queryset = Bookings.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        "id",
        "owner",
        "owner__id",
        "owner__is_driver",
        "owner__email",
        "owner__first_name",
        "owner__last_name",
        "booking_id",
        "is_active",
        "scheduled_date",
        "vehicle_type",
        "formated_address",
        "booking_receiver__name",
        "booking_receiver__phonenumber",
        "booking_product__product_type",
    )


class BookingUpdateApiView(GenericAPIView):
    """
    perform update on booking, requires booking id
    """

    permission_classes = [IsAdminUser]

    serializer_class = BookingSerializer

    def patch(self, request, *args, **kwargs):
        booking_id = request.data.get("id")
        booking = Bookings.objects.filter(id=booking_id).first()
        serializer = BookingSerializer(booking, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class BookingDeleteApiView(GenericAPIView):
    """
    deletes a specific booking, requires booking id
    """

    permission_classes = [IsAdminUser]

    serializer_class = BookingSerializer

    def delete(self, request, *args, **kwargs):
        id = request.data.get("id")
        if not id:
            msg = {"detail": "id is required for this operation"}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        booking = Bookings.objects.filter(id=id).first()
        if booking is not None:
            booking.delete()
            msg = {"detail": f"booking with id {id} deleted successfully"}
            return Response(msg)

        msg = {"detail": f"booking with id {id} does not exist"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)


class AdminDriverBankingInformationApiView(GenericAPIView):
    """
    get or add driver banking information
    """

    serializer_class = DriverBankingInformationSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        user = User.objects.filter(id=id).first()
        if user is not None:
            information = DriverBankingInformation.objects.filter(owner=user).first()
            serializer = DriverBankingInformationSerializer(information)
            return Response(serializer.data)

        msg = f"User with id {id}  does not exist"
        return Response(msg, status=status.HTTP_404_NOT_FOUND)
