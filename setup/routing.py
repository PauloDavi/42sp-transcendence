from django.urls import re_path

from apps.chat.consumers import ChatConsumer
from apps.matchmaking.game_consumer import AIDifficulty, PongConsumer
from apps.matchmaking.tictactoe_consumer import TicTacToeConsumer
from apps.matchmaking.tournament_consumer import TournamentConsumer
from apps.users.is_online_consumers import OnlineStatusConsumer
from apps.users.notification_consumer import NotificationConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/game/(?P<match_id>[^/]+)/(?P<single_player>single_player)?(?:/(?P<difficulty>easy|medium|hard))?/?$",
        PongConsumer.as_asgi(kwargs={"difficulty": AIDifficulty.MEDIUM.value}),
    ),
    re_path(r"ws/game/(?P<match_id>[0-9a-f-]+)/$", PongConsumer.as_asgi()),
    re_path(r"ws/tictactoe/(?P<match_id>[0-9a-f-]+)/$", TicTacToeConsumer.as_asgi()),
    re_path(r"ws/online-status/$", OnlineStatusConsumer.as_asgi()),
    re_path(r"ws/notifications/$", NotificationConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<room_uuid>[^/]+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/tournament/(?P<tournament_id>[0-9a-f-]+)/$", TournamentConsumer.as_asgi()),
]
