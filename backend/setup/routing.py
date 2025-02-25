from django.urls import re_path
from apps.users.consumers import OnlineStatusConsumer
from apps.matchmaking.consumers import PongConsumer
from apps.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/game/(?P<match_id>[0-9a-f-]+)/$", PongConsumer.as_asgi()),
    re_path(r"ws/online-status/$", OnlineStatusConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_uuid>[^/]+)/$', ChatConsumer.as_asgi()),
]
