import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.chat.models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.room_uuid = self.scope["url_route"]["kwargs"]["room_uuid"]
        self.room_group_uuid = f"chat_{self.room_uuid}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_uuid, self.channel_name)

        await self.accept()

    async def disconnect(self, message: dict) -> None:
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_uuid, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data: str) -> None:
        text_data_json = json.loads(text_data)
        message_content = text_data_json["message"]

        # Save message on postgres
        await sync_to_async(Message.objects.create)(
            sender=self.scope["user"],
            content=message_content,
            chat_id=self.room_uuid,
        )

        # Send message to room group
        await self.channel_layer.group_send(self.room_group_uuid, {"type": "chat.message", "message": message_content})

    # Receive message from room group
    async def chat_message(self, event: dict) -> None:
        message = event["message"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message}))
