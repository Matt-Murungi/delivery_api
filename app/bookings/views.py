from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.generics import GenericAPIView

from .serializers import BookingSerializer, ProductsSerializer, ReceiverSerializer
from .models import Bookings, ReceiverDetails, Products


class BookingsApiView(GenericAPIView):
    """
    get, create, update and delete bookings
    """

    permission_classes = [IsAuthenticated]

    serializer_class = BookingSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        bookings = Bookings.objects.filter(owner=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors)

    def patch(self, request, *args, **kwargs):
        booking = request.data.get("id")
        booking_ = Bookings.objects.filter(id=booking).first()
        if booking is not None:
            serializer = BookingSerializer(booking_, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                )
            else:
                return Response(serializer.errors)
        message = {"detail": f"No booking with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class BookingsAllApiView(GenericAPIView):
    """
    get all bookings
    """

    permission_classes = [IsAuthenticated]

    serializer_class = BookingSerializer

    def get(self, request, *args, **kwargs):
        bookings = Bookings.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class ConfirmBookingApiView(APIView):
    """
    get booking details (booking, product, receiver) using booking id
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        booking = Bookings.objects.filter(id=id).first()
        if booking is not None:
            product = Products.objects.filter(booking=booking).first()
            receiver = ReceiverDetails.objects.filter(booking=booking).first()
            booking_serializer = BookingSerializer(booking)
            product_serializer = ProductsSerializer(product)
            receiver_serializer = ReceiverSerializer(receiver)
            data = {
                "booking": booking_serializer.data,
                "product": product_serializer.data,
                "receiver": receiver_serializer.data,
            }
            return Response(data)
        message = {"detail": f"No booking with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class GetBookingApiView(GenericAPIView):
    """
    get booking, requires id
    """

    permission_classes = [IsAuthenticated]

    serializer_class = BookingSerializer

    def get(self, request, id, *args, **kwargs):
        booking = Bookings.objects.filter(id=id).first()
        serializer = BookingSerializer(booking)
        return Response(serializer.data)


class GetUserBookingsApi(GenericAPIView):
    """
    get all bookings by user
    """

    permission_classes = [IsAuthenticated]

    serializer_class = BookingSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        bookings = Bookings.objects.filter(owner=user)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)


class DeleteBookingApiView(APIView):
    """
    delete booking, requires id
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        id = request.data.get("id")

        if not id:
            msg = "Booking id is required for this operation"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        booking = Bookings.objects.filter(id=id).first()

        if not booking:
            msg = f"Booking id {id} does not exists"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        booking.delete()
        msg = "Booking deleted successfully"
        return Response(msg, status=status.HTTP_202_ACCEPTED)


class ReceiverApiView(GenericAPIView):
    """
    create, update and delete receiver
    """

    permission_classes = [IsAuthenticated]

    serializer_class = ReceiverSerializer

    def post(self, request, *args, **kwargs):
        serializer = ReceiverSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

    def patch(self, request, *args, **kwargs):
        id = request.data.get("id")
        receiver = ReceiverDetails.objects.filter(id=id).first()
        if receiver is not None:
            serializer = ReceiverSerializer(receiver, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                )
            else:
                return Response(serializer.errors)
        message = {"detail": f"No receiver with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class GetBookingReceiverApiView(GenericAPIView):
    """
    get booking receiver using id
    """

    permission_classes = [IsAuthenticated]

    serializer_class = ReceiverSerializer

    def get(self, request, id, *args, **kwargs):
        booking = Bookings.objects.filter(id=id).first()
        if booking is not None:
            receiver = ReceiverDetails.objects.filter(booking__id=id).first()
            serializer = ReceiverSerializer(receiver)
            return Response(serializer.data)
        message = {"detail": f"No booking with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class DeleteReceiverApiView(APIView):
    """
    delete receiver, requires id
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        id = request.data.get("id")

        if not id:
            msg = "Receiver id is required for this operation"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        receiver = ReceiverDetails.objects.filter(id=id).first()

        if not receiver:
            msg = f"Receiver with id {id} does not exist"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        receiver.delete()
        msg = "Receiver deleted successfully"
        return Response(msg, status=status.HTTP_202_ACCEPTED)


class ProductsApiView(GenericAPIView):
    """
    create, update and delete products
    """

    permission_classes = [IsAuthenticated]

    serializer_class = ProductsSerializer

    def post(self, request, *args, **kwargs):
        serializer = ProductsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
            )
        else:
            return Response(serializer.errors)

    def patch(self, request, *args, **kwargs):
        id = request.data.get("id")
        product = Products.objects.filter(id=id).first()
        if product is not None:
            serializer = ProductsSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    serializer.data,
                )
            else:
                return Response(serializer.errors)
        message = {"detail": f"No product with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class GetBookingProductApiView(GenericAPIView):
    """
    get products associated with a booking
    """

    permission_classes = [IsAuthenticated]

    serializer_class = ProductsSerializer

    def get(self, request, id, *args, **kwargs):
        products = Products.objects.filter(booking__id=id).first()
        serializer = ProductsSerializer(products)
        return Response(serializer.data)


class DeleteProductApiView(APIView):
    """
    delete product, requires id
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        id = request.data.get("id")
        if not id:
            msg = "Product id is required for this operation"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        product = Products.objects.filter(id=id).first()

        if not product:
            msg = f"Product with id {id} does not exist"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        product.delete()
        msg = "Product deleted successfully"
        return Response(msg, status=status.HTTP_202_ACCEPTED)


class GetAmountRange(GenericAPIView):
    """
    get various amounts for booking on different
    vehicles, requires booking id
    """

    permission_classes = [IsAuthenticated]

    serializer_class = BookingSerializer

    def get(self, request, id, *args, **kwargs):
        booking = Bookings.objects.filter(id=id).first()
        if booking is not None:
            data = booking.get_amount_range()
            if type(data) is str:
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            return Response(data)
        message = {"detail": f"No booking with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class ConfirmBookingReceiveApiView(GenericAPIView):
    """
    confirms reception of booking requires booking_id and otp
    """

    permission_classes = [IsAuthenticated]

    serializer_class = BookingSerializer

    def post(self, request, *args, **kwargs):
        booking_id = request.data.get("booking_id")
        otp = request.data.get("otp")
        if not booking_id:
            msg = "booking_id is required for this operation"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        if not otp:
            msg = "booking otp is required for this operation"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        booking = Bookings.objects.filter(id=booking_id).first()
        if not booking:
            msg = "booking_id entered does not exist"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        if booking.otp == otp:
            booking.is_confirmed = True
            booking.save()
            msg = "booking otp code confirmed successfully"
            return Response(msg, status=status.HTTP_200_OK)
        else:
            msg = "otp entered does not match the set booking otp"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)