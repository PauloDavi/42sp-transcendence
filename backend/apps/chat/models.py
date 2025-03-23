import uuid
from typing import ClassVar

from django.db import models

from apps.users.models import User


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True)
    is_group_chat = models.BooleanField(default=False)
    participants = models.ManyToManyField(User, through="ChatParticipants", related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering: ClassVar[list[str]] = ["-updated_at"]

    def __str__(self) -> str:
        return self.name if self.name else f"Chat {self.id}"


class ChatParticipants(models.Model):
    messages_not_read = models.IntegerField(default=0)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together: ClassVar[list[str]] = ["chat", "user"]

    def __str__(self) -> str:
        return f"{self.user} in {self.chat}"


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE, null=True)
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.sender}: {self.content[:50]}"


class BlockList(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    blocked = models.ForeignKey(User, related_name="blocked_user", on_delete=models.CASCADE)
    blocker = models.ForeignKey(User, related_name="blocker_user", on_delete=models.CASCADE)
