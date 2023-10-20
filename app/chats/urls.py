from django.urls import path

from .views import *

urlpatterns = [
    path("api/conversations/", ConversationApiView.as_view()),
    path("api/messages/<str:conversation_name>/", MessagesApiView.as_view()),
]
