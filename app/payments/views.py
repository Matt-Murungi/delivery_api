from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.http import JsonResponse
from asgiref.sync import sync_to_async
import asyncio
import os
import authorize
from operator import itemgetter

from rest_framework.generics import GenericAPIView

from .models import Order, Earnings, Payment, RequestEarnings, DriverBankingInformation
from .serializers import (
    CashPaymentSerializer,
    OrderSerializer,
    EarningsSerializer,
    PaymentSerializer,
    RequestEarningsSerializer,
    DriverBankingInformationSerializer,
)
from vehicles.models import Vehicle
from vehicles.serializers import VehicleSerializer
from users.models import User
from bookings.models import Bookings

api_login_id = os.environ.get("AUTHORIZE_API_LOGIN_ID")
api_transaction_key = os.environ.get("AUTHORIZE_TRANSACTION_KEY")

authorize.Configuration.configure(
    authorize.Environment.PRODUCTION,
    api_login_id,
    api_transaction_key,
)


class OwnerOrdersApiView(GenericAPIView):
    """
    get all orders associated to a user
    """

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(owner=user)
        serializer = OrderSerializer(orders, many=True)
        data = sorted(serializer.data, key=itemgetter("created_at"))
        return Response(data)


class DriverOrdersApiView(GenericAPIView):
    """
    get all orders associated to a driver
    """

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(driver=user)
        serializer = OrderSerializer(orders, many=True)
        data = sorted(serializer.data, key=itemgetter("created_at"), reverse=True)
        return Response(data)


class GetOrderApiView(GenericAPIView):
    """
    get order details using id
    """

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        order = Order.objects.filter(id=id).first()
        if order is not None:
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        message = {"detail": f"No order with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class ConfirmOrderPaymentApiView(APIView):
    """
    confirm order payment in cash
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, id, *args, **kwargs):
        order = Order.objects.filter(id=id).first()
        if order is not None:
            order.is_paid = True
            order.save()
            message = f"Order {id} payment confirmed successfully"
            return Response(message)
        message = {"detail": f"No order with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class GetOrdersApiView(GenericAPIView):
    """
    get all orders
    """

    permission_classes = [IsAuthenticated]

    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderApiView(GenericAPIView):
    """
    create, update order by client update order amount by vehicle type
    """

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        id = request.data.get("id")
        order = Order.objects.filter(id=id).first()
        if order is not None:
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        message = {"detail": f"No order with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class OngoingOrderApiView(GenericAPIView):
    """
    check whether user has ongoing order
    """

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        desired_statuses = ["1", "2", "3", "4"]
        order = Order.objects.filter(
            owner=request.user, status__in=desired_statuses
        ).last()
        if not order:
            message = {"detail": f"No order with id {id}"}
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetDriverApiView(APIView):
    """
    get driver for order with required vehicle, requires order id
    """

    serializer_class = VehicleSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        order = Order.objects.filter(id=id).first()
        if order is not None:
            vehicles = order.get_drivers()
            serializer = VehicleSerializer(vehicles, many=True)
            return Response(serializer.data)
        message = {"detail": f"No order with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class AcceptOrderApiView(GenericAPIView):
    """
    driver accepts order and order status is updated
    requires id of the order
    """

    permission_classes = [IsAuthenticated]

    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        id = request.data.get("order_id")
        vehicle_id = request.data.get("vehicle_id")
        user = request.user

        if not user.is_driver:
            msg = "You are not authorized to perform this action"
            return Response(msg, status=status.HTTP_403_FORBIDDEN)

        if not id:
            msg = "Please enter the order_id"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        if not vehicle_id:
            msg = "Please enter the vehicle_id"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        vehicle = Vehicle.objects.filter(id=vehicle_id).first()

        if not vehicle:
            msg = "The vehicle id you entered does not exist"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.filter(id=id).first()

        if not order:
            msg = "The order id you entered does not exist"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        if order.driver:
            msg = "This order is already taken"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)

        order.status = 2
        order.driver = user
        order.vehicle = vehicle
        order.save()
        order.booking.send_otp()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class DriverGetOrdersApiView(GenericAPIView):
    """
    get available orders for drivers
    """

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        orders = Order.objects.get_available_orders(request.user)
        data = []
        for order in orders:
            serializer = OrderSerializer(order).data
            data.append(serializer)
        data = sorted(data, key=itemgetter("created_at"))
        return Response(data)


class UpdateOrderStatusApiView(GenericAPIView):
    """
    driver updates order status
    """

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        id = request.data.get("id")
        order = Order.objects.filter(id=id).first()
        if order is not None:
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.data)
        message = {"detail": f"No order with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class EarningsApiView(GenericAPIView):
    """
    get user earnings
    """

    serializer_class = EarningsSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        earnings = Earnings.objects.filter(owner=user)
        serializer = EarningsSerializer(earnings, many=True)
        return Response(serializer.data)


class PaymentApiView(GenericAPIView):
    """
    get user payments
    """

    serializer_class = PaymentSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        payments = Payment.objects.filter(owner=user)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class GetPaymentApiview(GenericAPIView):
    """
    get payment by id
    """

    serializer_class = PaymentSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        payment = Payment.objects.filter(id=id).first()
        if payment is not None:
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        message = {"detail": f"No Payment with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class MakePaymentApiView(GenericAPIView):
    """
    make payment transaction and save payment
    """

    serializer_class = PaymentSerializer

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        pass


@sync_to_async()
def get_orders(id):
    orders = Order.objects.filter(id=1)[0]
    serializer = OrderSerializer(orders)
    data = serializer.data
    return data


@sync_to_async
def get_user(request):
    id = request.POST.get("user")
    if not id:
        raise ValueError("User id required for this operation")
    user = User.objects.filter(id=id).first()
    if not user:
        raise ValueError("User id entered does not exist")
    return user


@sync_to_async
def get_card_number(request):
    card_number = request.POST.get("card_number")
    return card_number


@sync_to_async
def get_card_code(request):
    card_code = request.POST.get("card_code")
    return card_code


@sync_to_async
def get_order_id(request):
    id = request.POST.get("order_id")
    if not id:
        raise ValueError("order_id is required for this operation")
    order = Order.objects.filter(id=int(id))
    if not order:
        raise ValueError(f"Order with id {id} does not exist")
    return id


@sync_to_async
def get_expiration_date(request):
    expiration = request.POST.get("expiration_date")
    return expiration


@sync_to_async
def get_amount(request):
    amount = request.POST.get("amount")
    return amount


@sync_to_async
def make_payment_task(user, card_number, card_code, expiration_date, amount, order_id):
    result = authorize.Transaction.sale(
        {
            "amount": amount[0],
            "email": user[0].email,
            "credit_card": {
                "card_number": card_number[0],
                "card_code": card_code[0],
                "expiration_date": expiration_date[0],
            },
            "order": {
                "invoice_number": order_id[0],
                "description": f"order {order_id[0]} invoice.",
            },
        }
    )
    return result


@sync_to_async
def save_payment(user, amount, trans_id, card_code, expiration_date, order_id):
    payment = Payment.objects.create(
        owner=user[0],
        amount=amount[0],
        transaction_id=trans_id,
        card_code=card_code[0],
        expiration_date=expiration_date[0],
        order_id=order_id[0],
    )
    payment.send_user_payment_notification(order_id[0])
    return payment


@sync_to_async
def update_order_payment_status(order_id):
    order = Order.objects.filter(id=order_id).first()
    order.is_paid = True
    order.save()
    return order


async def make_payment_request(request):
    """
    async function to make payment transaction and save payment
    requires: user (id), amount, card_number, card_code, expiration_date and order_id
    """
    try:
        user = await asyncio.gather(get_user(request))
    except ValueError as e:
        data = {"user": str(e)}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)

    card_number = await asyncio.gather(get_card_number(request))
    card_code = await asyncio.gather(get_card_code(request))
    expiration_date = await asyncio.gather(get_expiration_date(request))
    amount = await asyncio.gather(get_amount(request))
    order_id = await asyncio.gather(get_order_id(request))

    result = await asyncio.gather(
        make_payment_task(
            user, card_number, card_code, expiration_date, amount, order_id
        )
    )

    trans_id = result[0]["transaction_response"]["trans_id"]

    if trans_id:
        payment = await asyncio.gather(
            save_payment(user, amount, trans_id, card_code, expiration_date, order_id)
        )
    else:
        data = {"payment": "Payment was not successful"}
        return JsonResponse(data, status=status.HTTP_400_BAD_REQUEST)

    if payment:
        order_id = int(order_id[0])
        paid_order = await asyncio.gather(update_order_payment_status(order_id))
        if paid_order:
            data = {"data": "Payment was successful"}
        else:
            data = {"data": "Payment successful but order status not updated"}
    return JsonResponse(data, safe=False)


class CashPaymentApiView(GenericAPIView):
    """
    make cash payments
    """

    serializer_class = CashPaymentSerializer

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CashPaymentSerializer(data=request.data)
        if serializer.is_valid():
            order_id = request.data.get("order_id")
            order = Order.objects.filter(id=order_id).first()
            order.is_paid = True
            order.save()
            amount = order.get_payment_charge()
            user = request.user
            payment = Payment.objects.create(
                owner=user, order_id=order.id, amount=amount
            )
            serializer = PaymentSerializer(payment)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class GetOrderAmountApiView(GenericAPIView):
    """
    get adn update order amount for payment, requires order id
    """

    serializer_class = OrderSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        order = Order.objects.filter(id=id).first()
        if not order:
            data = {"Order": f"Order with id {id} does not exist"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        receiver = order.booking.booking_receiver
        if not receiver:
            data = {"Order": "Order booking requires a receiver first"}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        serializer = OrderSerializer(order)
        return Response(serializer.data)


class DriverBankingInformationApiView(GenericAPIView):
    """
    get or add driver banking information
    """

    serializer_class = DriverBankingInformationSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        information = DriverBankingInformation.objects.filter(owner=user).first()
        serializer = DriverBankingInformationSerializer(information)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = DriverBankingInformationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class UpdateDriverBankingInformationApiView(GenericAPIView):
    "update/patch driver banking information"

    serializer_class = DriverBankingInformationSerializer

    permission_classes = [IsAuthenticated]

    def patch(self, request, id, *args, **kwargs):
        info = DriverBankingInformation.objects.filter(id=id).first()
        if info is not None:
            serializer = DriverBankingInformationSerializer(
                info, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        message = {"detail": f"No banking information with id {id}"}
        return Response(message, status=status.HTTP_404_NOT_FOUND)


class RequestEarningsApiView(GenericAPIView):
    """
    request for earnings, requires owner (user id) and amount
    can also get previous requests
    """

    serializer_class = RequestEarningsSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        earnings_request = RequestEarnings.objects.filter(owner=user)
        serializer = RequestEarningsSerializer(earnings_request, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = RequestEarningsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.data)


class UserCancelOrderApiView(APIView):
    """
    deletes a user order requires the booking id
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        booking_id = request.data.get("booking_id")
        if not booking_id:
            msg = "Please enter the booking_id"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        booking = Bookings.objects.filter(id=booking_id).first()
        if not booking:
            msg = f"Booking with id {booking_id} does not exist"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        booking.delete()
        data = "Your Booking has been deleted successfully"
        return Response(data)


class DriverCancelOrderApiView(APIView):
    """
    driver cancels taking current order, requires order_id
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        if not order_id:
            msg = "Please enter the order_id"
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.filter(id=order_id).first()
        if not order:
            msg = f"Order with id {order_id} does not exist"
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        order.driver = None
        order.save()
        data = "The Order has been canceled successfully"
        return Response(data)


class DriverPaymentApiView(APIView):
    """
    check whether a certain order is paid or not requires id
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        if not id:
            raise ValueError("order_id is required")
        transaction = Payment.objects.filter(order_id=id).first()
        if not transaction:
            msg = {"is_paid": False}
            return Response(msg)
        msg = {"is_paid": True}
        return Response(msg)
