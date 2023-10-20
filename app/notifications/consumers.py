from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save
from django.dispatch import receiver
import channels.layers

from .models import Notification, PeopleOnline, OnlineDrivers
from .serializers import (
    NotificationSerializer,
    PeopleOnlineSerializer,
    DriverSerializer,
)
from chats.models import Message
from chats.serializers import MessageSerializer
from payments.models import Order
from payments.serializers import OrderSerializer
from users.models import User
from users.serializers import UserSerializer


class NotificationConsumer(JsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.notification_group_name = None
        self.people_online = None

    def connect(self):
        self.user = self.scope["user"]
        print("User is ", self.user)
        if not self.user.is_authenticated:
            return

        self.accept()

        self.people_online = PeopleOnline.objects.get_or_create(id=1)[0]

        self.notification_group_name = str(self.user.id) + "__notifications"

        async_to_sync(self.channel_layer.group_add)(
            self.notification_group_name,
            self.channel_name,
        )

        count = Message.objects.filter(receiver=self.user, is_read=False).count()
        self.send_json(
            {
                "type": "unread_count",
                "msg_count": count,
            }
        )

        self.people_online.online.add(self.user)

    def unread_count(self, event):
        self.send_json(event)

    def new_message_notification(self, event):
        self.send_json(event)

    def disconnect(self, code):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.people_online.online.remove(self.user)

        async_to_sync(self.channel_layer.group_discard)(
            self.notification_group_name,
            self.channel_name,
        )
        return super().disconnect(code)

    def send_user_notification(self, event):
        self.send_json(event)

    def send_drivers_notification(self, event):
        self.send_json(event)

    def receive_json(self, content, **kwargs):
        message_type = content["type"]

        if message_type == "get_notifications":
            notifications = Notification.objects.filter(owner=self.user)

            async_to_sync(self.channel_layer.group_send)(
                self.notification_group_name,
                {
                    "type": "get_notifications",
                    "name": self.notification_group_name,
                    "message": NotificationSerializer(notifications, many=True).data,
                },
            )

        if message_type == "get_online_people":
            online_people = PeopleOnline.objects.all()

            async_to_sync(self.channel_layer.group_send)(
                self.notification_group_name,
                {
                    "type": "get_online_people",
                    "name": self.notification_group_name,
                    "message": PeopleOnlineSerializer(online_people, many=True).data,
                },
            )

        if message_type == "add_location":
            driver_location, created = OnlineDrivers.objects.get_or_create(
                driver=self.user
            )
            driver_location.latitude = content["latitude"]
            driver_location.longitude = content["longitude"]
            driver_location.formated_address = content["formated_address"]
            driver_location.save()

            async_to_sync(self.channel_layer.group_send)(
                self.notification_group_name,
                {
                    "type": "add_location",
                    "name": self.notification_group_name,
                    "message": "Location updated",
                    "result": DriverSerializer(driver_location).data,
                },
            )

    def add_location(self, event):
        self.send_json(event)

    def get_online_people(self, event):
        self.send_json(event)

    def get_notifications(self, event):
        self.send_json(event)

    def order_notifications(self, event):
        self.send_json(event)
