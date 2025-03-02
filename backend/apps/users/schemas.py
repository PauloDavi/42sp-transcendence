from dataclasses import dataclass
from typing import Any
from uuid import UUID

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


@dataclass
class ToastMessage:
    title: str
    message: str
    tag: str
    action: str | None = None
    extra_data: dict[str, Any] | None = None

    def to_dict(self) -> dict:
        return {
            "type": "send_toast",
            "title": self.title,
            "message": self.message,
            "tag": self.tag,
            "action": self.action,
            "extra_data": self.extra_data,
        }

    def send_to_group(self, user_id: UUID) -> dict:
        channel_layer = get_channel_layer()
        return async_to_sync(channel_layer.group_send)(
            str(user_id),
            self.to_dict(),
        )
