from rest_framework import serializers

from .models import Order, Earnings, DriverBankingInformation, RequestEarnings, Payment
from users.serializers import UserSerializer
from bookings.serializers import BookingSerializer
from vehicles.serializers import VehicleSerializer


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["booking"] = BookingSerializer(read_only=True)
        self.fields["owner"] = UserSerializer(read_only=True)
        self.fields["driver"] = UserSerializer(read_only=True)
        self.fields["vehicle"] = VehicleSerializer(read_only=True)
        return super(OrderSerializer, self).to_representation(instance)


class EarningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Earnings
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["owner"] = UserSerializer(read_only=True)
        return super(EarningsSerializer, self).to_representation(instance)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["booking"] = BookingSerializer(read_only=True)
        self.fields["owner"] = UserSerializer(read_only=True)
        return super(PaymentSerializer, self).to_representation(instance)


class RequestEarningsSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestEarnings
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["owner"] = UserSerializer(read_only=True)
        self.fields["order"] = OrderSerializer(read_only=True)
        return super(RequestEarningsSerializer, self).to_representation(instance)


class DriverBankingInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverBankingInformation
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["owner"] = UserSerializer(read_only=True)
        return super(DriverBankingInformationSerializer, self).to_representation(
            instance
        )


class CashPaymentSerializer(serializers.Serializer):
    order_id = serializers.CharField(required=True)

    def validate_order_id(self, value):
        if value is not None:
            order_exists = Order.objects.filter(id=value).exists()
            if not order_exists:
                msg = "Order with entered id does not exist"
                raise serializers.ValidationError(msg)
        return value
