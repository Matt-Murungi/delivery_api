from django.db.models import Q
from django.db import models

from users.models import User


class ConversationManager(models.Manager):
    def get_user_chat(self, user_1, user_2):
        look_up = Q(name__icontains=user_1) & Q(name__icontains=user_2)
        return self.model.objects.filter(look_up).distinct()

    def get_user_conversations(self, user):
        look_up = Q(name__icontains=user.id)
        return self.model.objects.filter(look_up).distinct()


class Conversation(models.Model):
    name = models.CharField(max_length=207)
    online = models.ManyToManyField(to=User, blank=True)

    objects = ConversationManager()

    def get_online_count(self):
        return self.online.user.count()

    def join(self, user):
        self.online.add(user)
        self.save()

    def leave(self, user):
        self.online.remove(user)
        self.save()

    def __str__(self):
        return self.name


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="conversation_message"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="message_sender"
    )
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="message_receiver"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.sender.email
