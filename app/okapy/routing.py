from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chats.middleware import TokenAuthMiddleware
from django.core.asgi import get_asgi_application

from chats.routing import websocket_routes


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": TokenAuthMiddleware(URLRouter(websocket_routes)),
    }
)
