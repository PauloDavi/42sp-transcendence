from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from apps.matchmaking.models import Match, Tournament, TournamentPlayer
from apps.users.models import User


class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        pass

    async def disconnect(self, message: dict) -> None:
        pass

    async def receive(self, text_data: str) -> None:
        pass


@database_sync_to_async
def verify_if_user_in_match(match: Match, user: User) -> bool:
    return user in {match.user1, match.user2}
