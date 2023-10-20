from rest_framework import serializers

from .models import Bookings, ReceiverDetails, Products
from users.serializers import UserSerializer


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["owner"] = UserSerializer(read_only=True)
        return super(BookingSerializer, self).to_representation(instance)


class ReceiverSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReceiverDetails
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["booking"] = BookingSerializer(read_only=True)
        return super(ReceiverSerializer, self).to_representation(instance)


class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["booking"] = BookingSerializer(read_only=True)
        return super(ProductsSerializer, self).to_representation(instance)
