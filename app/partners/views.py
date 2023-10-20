from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.authtoken.models import Token

from .models import Partner, PartnerProduct, ProductCategory
from users.serializers import UserSerializer
from bookings.models import Bookings, Products
from payments.models import Order, Payment
from .serializers import (
    PartnerSerializer,
    PartnerProductSerializer,
    ProductCategorySerializer,
)
from payments.serializers import PaymentSerializer
from bookings.serializers import (
    ProductsSerializer,
    BookingSerializer,
    ReceiverSerializer,
)
from bookings.models import ReceiverDetails
from payments.serializers import OrderSerializer
from users.serializers import LoginSerializer
from core.libs.errors import (
    partner_non_existant,
    invalid_user,
    email_not_existant,
    not_a_partner,
    generate_error_for_not_existant,
    generate_error_for_already_exists,
)

User = get_user_model()


class GetPatnerApiView(GenericAPIView):
    """
    get partner by id
    """

    serializer_class = PartnerSerializer

    def get(self, request, id, *args, **kwargs):
        partner = Partner.objects.filter(id=id).first()
        if partner is not None:
            serializer = PartnerSerializer(partner)
            return Response(data=serializer.data)
        message = {"detail": f"No partner with id {id}"}
        return Response(data=message, status=status.HTTP_404_NOT_FOUND)


class PartnerView(GenericAPIView):
    """
    get all Partners
    """

    serializer_class = PartnerSerializer

    def get(self, request, *args, **kwargs):
        partners = Partner.objects.all()
        serializer = PartnerSerializer(partners, many=True)
        return Response(data=serializer.data)


class PartnerOwnerApiView(GenericAPIView):
    """
    get, update and delete Partner as owner
    """

    serializer_class = PartnerSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        partner_obj = Partner.objects.filter(owner=user)
        if partner_obj.count() < 1:
            data = {"Partners": ["You dont have any yet"]}
            return Response(data=data, status=status.HTTP_204_NO_CONTENT)
        serializer = PartnerSerializer(partner_obj, many=True)
        return Response(data=serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = PartnerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors)

    def patch(self, request, *args, **kwargs):
        id = request.data.get("id")
        partner = Partner.objects.filter(id=id).first()
        if partner is not None:
            serializer = PartnerSerializer(partner, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data)
            else:
                return Response(data=serializer.errors)
        message = {"detail": f"No partner with id {id}"}
        return Response(data=message, status=status.HTTP_404_NOT_FOUND)


class DeletePartnerApiView(APIView):
    """
    delete partner, requires partner
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        id = request.data.get("id")

        if not id:
            msg = "Partner id is required for this operation"
            return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

        partner = Partner.objects.filter(id=id).first()

        if not partner:
            msg = f"Partner with id {id} does not exist"
            return Response(data=msg, status=status.HTTP_400_BAD_REQUEST)

        partner.delete()
        msg = "Partner deleted successfully"
        return Response(data=msg, status=status.HTTP_202_ACCEPTED)


class PartnerAuthenticationView(APIView):
    """
    Authenticate partner in the dashboard
    """

    def post(self, request):

        try:
            if not request.data["email"]:
                return Response(
                    data=email_not_existant, status=status.HTTP_400_BAD_REQUEST
                )
            user_serializer = LoginSerializer(data=request.data)
            if not user_serializer.is_valid():
                return Response(
                    data=user_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

            user = (
                get_user_model()
                .objects.filter(email=user_serializer.validated_data["email"])
                .first()
            )
            user_serialized_obj = UserSerializer(user)
            print(user_serialized_obj)
            partner = Partner.objects.filter(id=user.partner.id).first()
            if not partner:
                return Response(
                    data=partner_non_existant, status=status.HTTP_400_BAD_REQUEST
                )
            partner_serializer = PartnerSerializer(partner)

            token = Token.objects.filter(user=user).first()
            if not token:
                return Response(data=invalid_user, status=status.HTTP_400_BAD_REQUEST)
            data = {
                "partner": partner_serializer.data,
                "user": user_serialized_obj.data,
                "token": token.key,
            }
            return Response(
                data=data,
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                data={"detail": f"Internal Server Error {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PartnerProductApiView(GenericAPIView):
    """create, retrieve, delete and update the partner products"""

    permission_classes = [IsAuthenticated]
    serializer_class = PartnerProductSerializer

    def get(self, request, *args, **kwargs):
        partner = request.user.partner.id
        if not partner or partner is None:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)
        product_obj = (
            PartnerProduct.objects.filter(partner=partner)
            .filter(is_deleted=False)
            .order_by("-date_created")
        )
        serializer = PartnerProductSerializer(product_obj, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        partner = request.user.partner.id
        product_obj = PartnerProduct.objects.filter(
            name__iexact=request.data["name"]
        ).filter(is_deleted=False)
        if product_obj.exists() and product_obj.first().partner.id == partner:
            return Response(
                data=generate_error_for_already_exists(request.data["name"]),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = PartnerProductSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class PartnerProductGetApiView(GenericAPIView):
    """Retrieve partner products"""

    permission_classes = [IsAuthenticated]
    serializer_class = PartnerProductSerializer

    def get(self, request, id, *args, **kwargs):
        product_obj = PartnerProduct.objects.filter(partner=id)
        if product_obj is None:
            return Response(
                data=generate_error_for_not_existant("Products "),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = PartnerProductSerializer(product_obj, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, id, *args, **kwargs):
        partner = request.user.partner.id
        patching_payload = {}

        if not partner or partner is None:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)
        for item, key in request.data.items():
            if key:
                patching_payload[item] = key
        product_obj = PartnerProduct.objects.filter(id=id).first()
        serializer = PartnerProductSerializer(
            product_obj, data=patching_payload, partial=True
        )
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AllPartnerProductApiView(GenericAPIView):
    """Retrieve all partner products"""

    permission_classes = [IsAuthenticated]
    serializer_class = PartnerProductSerializer

    def get(self, request, id, *args, **kwargs):
        product_obj = (
            PartnerProduct.objects.filter(partner=id)
            .filter(is_deleted=False)
            .filter(is_active=True)
        )
        serializer = PartnerProductSerializer(product_obj, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CustomerProductAPIView(APIView):
    """
    Concerning products from the customer's side
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Post multiple products made by the user
        """
        products_data = request.data.get("products")
        booking_id = request.data["booking"]
        print(f"products {products_data}")

        booking = Bookings.objects.filter(booking_id=booking_id).first()
        if not booking:
            return Response(
                data=generate_error_for_not_existant("booking "),
                status=status.HTTP_400_BAD_REQUEST,
            )

        products = []
        for name, quantity in products_data.items():
            product = Products(booking=booking, name=name, quantity=quantity)
            products.append(product)
        Products.objects.bulk_create(products)

        serializer = ProductsSerializer(products, many=True)
        if not serializer.data:
            Bookings.objects.delete(booking_id=booking_id)
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """
        Get all booking products made by user to the partner
        """
        partner = request.user.partner.id
        if not partner or partner is None:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)

        product_obj = Products.objects.filter(booking__partner=partner)
        serializer = ProductsSerializer(product_obj, many=True)

        if not serializer:
            return Response(
                data=generate_error_for_not_existant("Product"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductCategoryApiView(GenericAPIView):
    """create, retrieve, delete and update the partner product categories"""

    permission_classes = [IsAuthenticated]
    serializer_class = ProductCategorySerializer

    def get(self, request, *args, **kwargs):
        """
        Get all partner product categories
        """
        partner = request.user.partner.id
        if not partner or partner is None:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)
        product_obj = ProductCategory.objects.filter(partner=partner).filter(
            is_deleted=False
        )
        serializer = ProductCategorySerializer(product_obj, many=True)
        if not serializer:
            return Response(
                data=generate_error_for_not_existant("Product"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Create a partner product category
        """
        partner = request.user.partner.id
        if not partner:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)
        product_category_obj = ProductCategory.objects.filter(
            name__iexact=request.data["name"]
        )

        if product_category_obj.exists() or product_category_obj:
            return Response(
                data=generate_error_for_already_exists(request.data["name"]),
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.data["partner"] = partner

        serializer = ProductCategorySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(data="serializer.data", status=status.HTTP_201_CREATED)

    def patch(self, request, *args, **kwargs):
        """
        Update a partner product category
        """
        partner = request.user.partner.id
        category = request.data["id"]

        if partner is not request.data["partner"] or not partner or partner is None:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)

        product_category_obj = ProductCategory.objects.filter(id=category).first()
        serializer = ProductCategorySerializer(
            product_category_obj, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PartnerOrderAPIView(APIView):
    """
    Get booking details (booking, product, receiver) belonging to that booking
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, id, *args, **kwargs):
        partner = request.user.partner.id
        if not partner or partner is None:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)

        booking = Bookings.objects.filter(id=id).first()
        if booking is not None:
            product = Products.objects.filter(booking=booking)
            receiver = ReceiverDetails.objects.filter(booking=booking).first()
            booking_serializer = BookingSerializer(booking)
            product_serializer = ProductsSerializer(product, many=True)
            receiver_serializer = ReceiverSerializer(receiver)
            data = {
                "booking": booking_serializer.data,
                "product": product_serializer.data,
                "receiver": receiver_serializer.data,
            }
            return Response(data=data)
        message = {"detail": f"No booking with id {id}"}
        return Response(data=message, status=status.HTTP_404_NOT_FOUND)


class PartnerOrdersStatusApiView(GenericAPIView):
    """
    Concerning all orders based on their status
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        """
        Update order status
        """
        partner = request.user.partner.id
        id = request.data.get("id")
        order_status = request.data.get("status")
        if not partner or partner is None:
            return Response(data=not_a_partner, status=400)
        if not id:
            return Response(
                data=generate_error_for_not_existant("Order id"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        order = Order.objects.filter(id=id).first()

        if not order:
            return Response(
                data=generate_error_for_not_existant("Order"),
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrderSerializer(order)
        if not serializer.data:
            return Response(
                data="Unable to make request", status=status.HTTP_400_BAD_REQUEST
            )
        order.status = order_status
        order.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        """
        Get all orders with all statuses
        """
        partner = request.user.partner.id
        if not partner or partner is None:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.filter(booking__partner=partner)
        if not order:
            return Response(
                data=generate_error_for_not_existant("Order "),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = OrderSerializer(order, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PartnerOrderStatusApiView(GenericAPIView):
    """
    Concerning all orders based on their status
    """

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get(self, request, id, *args, **kwargs):
        """
        Get a product by order status
        """
        partner = request.user.partner.id
        status_id = id
        if not partner or partner is None:
            return Response(data=not_a_partner, status=status.HTTP_400_BAD_REQUEST)

        if not status_id:
            order = Order.objects.filter(booking__partner=partner)
            if not order:
                return Response(
                    data=generate_error_for_not_existant("Order "),
                    status=status.HTTP_400_BAD_REQUEST,
                )
            serializer = OrderSerializer(order, many=True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)

        order = Order.objects.filter(booking__partner=partner).filter(status=status_id)
        if not order:
            return Response(
                data=generate_error_for_not_existant("Order "),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = OrderSerializer(order, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)


class PartnerPaymentsApiView(GenericAPIView):
    """
    All customer payments belonging to partner
    """

    serializer_class = PaymentSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        partner = User.objects.get(email=user).partner
        if not partner:
            return Response(
                data=generate_error_for_not_existant("user"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        payments = Payment.objects.filter(order__booking__partner=partner)
        if not payments:
            return Response(
                data=generate_error_for_not_existant("payments"),
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = PaymentSerializer(payments, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
