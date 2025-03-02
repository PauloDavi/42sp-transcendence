import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        if "user" in self.scope and self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            await self.channel_layer.group_add(str(self.user.id), self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, message: dict) -> None:
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(str(self.user.id), self.channel_name)

    async def send_toast(self, event: dict) -> None:
        await self.send(text_data=json.dumps(event))
