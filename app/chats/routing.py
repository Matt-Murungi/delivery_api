from django.urls import re_path

from .consumers import ChatConsumer
from notifications.consumers import NotificationConsumer

websocket_routes = [
    re_path(r"^chats/(?P<conversation_name>[^/]+)/$", ChatConsumer.as_asgi()),
    re_path("notifications/", NotificationConsumer.as_asgi()),
]
