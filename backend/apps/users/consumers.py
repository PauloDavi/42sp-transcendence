import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.users.models import User


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        if "user" in self.scope and self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            await self.channel_layer.group_add(str(self.user.id), self.channel_name)
            await update_status_online(self.user, status_online=True)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, message: dict) -> None:
        if self.user.is_authenticated:
            await update_status_online(self.user, status_online=False)
            await self.channel_layer.group_discard(str(self.user.id), self.channel_name)

    async def send_toast(self, event: dict) -> None:
        await self.send(text_data=json.dumps(event))


@database_sync_to_async
def update_status_online(user: User, status_online: bool) -> None:
    user.status_online = status_online
    user.save()
