from rest_framework import serializers

from .models import *
from users.serializers import UserSerializer


class DriverRatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverRating
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["driver"] = UserSerializer(read_only=True)
        self.fields["owner"] = UserSerializer(read_only=True)
        return super(DriverRatingsSerializer, self).to_representation(instance)
