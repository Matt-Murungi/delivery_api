from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token

from users.models import User
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user(scope):
    """
    Return the user model instance associated with the given scope.
    If no user is retrieved, return an instance of `AnonymousUser`.
    """

    if "token" not in scope:
        raise ValueError("Cannot find token in scope.")
    key = scope["token"]

    try:
        token = Token.objects.select_related("user").get(key=key)
    except Token.DoesNotExist:
        raise AuthenticationFailed("Invalid token.")

    user = token.user

    return user or AnonymousUser()


class TokenAuthMiddleware:
    """
    middleware that takes a token from the query string and authenticates auth token.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_params = parse_qs(scope["query_string"].decode())
        token = query_params["token"][0]
        scope["token"] = token
        scope["user"] = await get_user(scope)
        return await self.app(scope, receive, send)
