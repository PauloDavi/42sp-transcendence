from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json


class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.user = self.scope["user"]
            await self.channel_layer.group_add(str(self.user.id), self.channel_name)
            await update_status_online(self.user, True)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await update_status_online(self.user, False)
            await self.channel_layer.group_discard(str(self.user.id), self.channel_name)

    async def send_toast(self, event):
        await self.send(text_data=json.dumps(event))


@database_sync_to_async
def update_status_online(user, status_online):
    user.status_online = status_online
    user.save()
