from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import GenericAPIView

from .models import Message, Conversation
from .serializers import MessageSerializer, ConversationSerializer


class MessagesApiView(GenericAPIView):
    """
    get messages from conversation name
    """

    permission_classes = [IsAuthenticated]

    serializer_class = MessageSerializer

    def get(self, request, conversation_name, *args, **kwargs):
        mesages = Message.objects.filter(conversation__name=conversation_name).order_by(
            "-created_at"
        )
        serializer = MessageSerializer(mesages, many=True)
        return Response(serializer.data)


class ConversationApiView(GenericAPIView):
    """
    get conversation associated with user
    """

    permission_classes = [IsAuthenticated]

    serializer_class = ConversationSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        conversations = Conversation.objects.get_user_conversations(user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)
