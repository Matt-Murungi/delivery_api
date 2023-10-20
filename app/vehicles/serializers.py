from rest_framework import serializers

from .models import *
from users.serializers import UserSerializer


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["owner"] = UserSerializer(read_only=True)
        return super(VehicleSerializer, self).to_representation(instance)
