from django.urls import re_path

from apps.chat.consumers import ChatConsumer
from apps.matchmaking.consumers import PongConsumer
from apps.users.consumers import OnlineStatusConsumer

websocket_urlpatterns = [
    re_path(r"ws/game/(?P<match_id>[0-9a-f-]+)/$", PongConsumer.as_asgi()),
    re_path(r"ws/online-status/$", OnlineStatusConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<room_uuid>[^/]+)/$", ChatConsumer.as_asgi()),
]
