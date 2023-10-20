from rest_framework import serializers

from .models import *
from users.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["owner"] = UserSerializer(read_only=True)
        return super(NotificationSerializer, self).to_representation(instance)


class PeopleOnlineSerializer(serializers.ModelSerializer):
    online = UserSerializer(read_only=True, many=True)

    class Meta:
        model = PeopleOnline
        fields = "__all__"


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineDrivers
        fields = "__all__"

    def to_representation(self, instance):
        self.fields["driver"] = UserSerializer(read_only=True)
        return super(DriverSerializer, self).to_representation(instance)
