from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync

from users.models import User
from .models import Conversation, Message
from .serializers import MessageSerializer


class ChatConsumer(JsonWebsocketConsumer):
    """
    This consumer is used to send messages.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.user = None
        self.conversation_name = None
        self.conversation = None

    def connect(self):
        print("Connected!")
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        self.accept()
        self.conversation_name = self.scope["url_route"]["kwargs"]["conversation_name"]

        user_1 = self.user.id
        user_2 = self.get_receiver().id

        convo = Conversation.objects.get_user_chat(user_1, user_2)

        if convo:
            self.conversation = convo[0]
            self.conversation_name = convo[0].name

        else:
            conv = Conversation.objects.create(name=self.conversation_name)
            self.conversation = conv

        async_to_sync(self.channel_layer.group_add)(
            self.conversation_name,
            self.channel_name,
        )

        self.send_json(
            {
                "type": "online_user_list",
                "users": [user.email for user in self.conversation.online.all()],
            }
        )

        async_to_sync(self.channel_layer.group_send)(
            self.conversation_name,
            {
                "type": "user_join",
                "user": self.user.email,
            },
        )

        self.conversation.online.add(self.user)

        self.send_json(
            {
                "type": "welcome_message",
                "message": f"{self.conversation_name}",
            }
        )

    def user_join(self, event):
        self.send_json(event)

    def disconnect(self, code):
        print("Disconnected!")
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            return

        async_to_sync(self.channel_layer.group_send)(
            self.conversation_name,
            {
                "type": "user_leave",
                "user": self.user.email,
            },
        )

        self.conversation.online.remove(self.user)

        return super().disconnect(code)

    def user_leave(self, event):
        self.send_json(event)

    def receive_json(self, content, **kwargs):
        message_type = content["type"]
        if message_type == "chat_message":

            message = Message.objects.create(
                sender=self.user,
                receiver=self.get_receiver(),
                text=content["message"],
                conversation=self.conversation,
            )

            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "chat_message_echo",
                    "name": content["name"],
                    "message": MessageSerializer(message).data,
                },
            )

            notification_group_name = str(self.get_receiver().id) + "__notifications"
            async_to_sync(self.channel_layer.group_send)(
                notification_group_name,
                {
                    "type": "new_message_notification",
                    "name": self.conversation_name,
                    "message": MessageSerializer(message).data,
                },
            )

        if message_type == "get_messages":

            messages = Message.objects.filter(conversation=self.conversation).order_by(
                "-created_at"
            )

            async_to_sync(self.channel_layer.group_send)(
                self.conversation_name,
                {
                    "type": "last_messages",
                    "name": self.conversation_name,
                    "message": MessageSerializer(messages, many=True).data,
                },
            )

        if message_type == "read_messages":

            messages_to_me = messages = Message.objects.filter(
                conversation=self.conversation, receiver=self.user
            )
            messages_to_me.update(is_read=True)

            unread_count = Message.objects.filter(
                receiver=self.user, is_read=False
            ).count()
            async_to_sync(self.channel_layer.group_send)(
                str(self.user.id) + "__notifications",
                {
                    "type": "unread_count",
                    "msg_count": unread_count,
                },
            )

        return super().receive_json(content, **kwargs)

    def unread_count(self, event):
        self.send_json(event)

    def new_message_notification(self, event):
        self.send_json(event)

    def last_messages(self, event):
        self.send_json(event)

    def chat_message_echo(self, event):
        self.send_json(event)

    def get_receiver(self):
        ids = self.conversation_name.split("__")
        for id_ in ids:
            if id_ != str(self.user.id):
                return User.objects.get(id=id_)
