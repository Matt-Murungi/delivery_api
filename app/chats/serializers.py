from rest_framework import serializers

from .models import *
from users.serializers import UserSerializer


class ConversationSerializer(serializers.ModelSerializer):
    online = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Conversation
        fields = "__all__"


class MessageSerializer(serializers.ModelSerializer):
    conversation = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = "__all__"

    def get_conversation(self, obj):
        return str(obj.conversation.name)

    def to_representation(self, instance):
        self.fields["sender"] = UserSerializer(read_only=True)
        self.fields["receiver"] = UserSerializer(read_only=True)
        return super(MessageSerializer, self).to_representation(instance)
