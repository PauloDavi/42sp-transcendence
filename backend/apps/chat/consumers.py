import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.formats import date_format
from django.utils.timezone import localtime

from apps.chat.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.room_uuid = self.scope["url_route"]["kwargs"]["room_uuid"]
        self.room_group_uuid = f"chat_{self.room_uuid}"
        await self.channel_layer.group_add(self.room_group_uuid, self.channel_name)
        await self.accept()

    async def disconnect(self, message: dict) -> None:
        await self.channel_layer.group_discard(self.room_group_uuid, self.channel_name)

    async def receive(self, text_data: str) -> None:
        text_data_json = json.loads(text_data)
        message_content = text_data_json["message"]
        message = await sync_to_async(Message.objects.create)(
            sender=self.scope["user"],
            content=message_content,
            chat_id=self.room_uuid,
        )

        await self.channel_layer.group_send(
            self.room_group_uuid,
            {
                "type": "chat.message",
                "message": {
                    "sender_id": str(message.sender.id),
                    "sender_avatar": message.sender.avatar.url,
                    "content": message.content,
                    "send_at": date_format(localtime(message.sent_at), "d/m/Y H:i:s"),
                },
            },
        )

    async def chat_message(self, event: dict) -> None:
        message = event["message"]
        await self.send(text_data=json.dumps({"message": message}))
