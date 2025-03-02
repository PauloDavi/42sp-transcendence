import json
import random
from typing import ClassVar
from uuid import UUID

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Q
from django.utils.timezone import now

from apps.matchmaking.models import Match, Tournament, TournamentBye, TournamentPlayer

MIN_TOURNAMENT_PLAYERS = 3


class TournamentConsumer(AsyncWebsocketConsumer):
    connected_users: ClassVar[dict[str, set[str]]] = {}

    async def connect(self) -> None:
        self.tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
        self.tournament_group_name = f"tournament_{self.tournament_id}"
        self.user = self.scope["user"]

        if self.tournament_group_name not in self.connected_users:
            self.connected_users[self.tournament_group_name] = set()

        self.connected_users[self.tournament_group_name].add(str(self.user.id))

        await self.channel_layer.group_add(self.tournament_group_name, self.channel_name)
        await self.accept()

        await self.update_players_status()

    async def disconnect(self, close_code: int) -> None:
        if self.tournament_group_name in self.connected_users:
            self.connected_users[self.tournament_group_name].discard(str(self.user.id))

        if not self.connected_users[self.tournament_group_name]:
            del self.connected_users[self.tournament_group_name]

        await self.channel_layer.group_discard(self.tournament_group_name, self.channel_name)

        await self.update_players_status()

    async def update_players_status(self) -> None:
        players = await self.get_tournament_players_with_status()
        await self.channel_layer.group_send(
            self.tournament_group_name,
            {"type": "tournament_message", "message": {"action": "players_status_update", "players": players}},
        )

    @database_sync_to_async
    def get_tournament_players_with_status(self) -> list[dict]:
        tournament = Tournament.objects.get(id=self.tournament_id)
        connected_users = self.connected_users.get(self.tournament_group_name, set())

        active_matches = tournament.matches.filter(winner__isnull=True)
        players_in_match = set()

        for match in active_matches:
            players_in_match.add(str(match.user1.id))
            players_in_match.add(str(match.user2.id))

        return [
            {
                "id": str(player.player.id),
                "username": player.player.username,
                "display_name": player.display_name,
                "is_connected": str(player.player.id) in connected_users,
                "in_match": str(player.player.id) in players_in_match,
            }
            for player in tournament.players.all()
        ]

    async def receive(self, text_data: str) -> None:
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start_matches":
            await self.start_tournament_matches()

    async def start_tournament_matches(self) -> None:
        tournament = await self.get_tournament()
        if tournament.started_at:
            return

        connected_players = await self.get_connected_players()
        if len(connected_players) < MIN_TOURNAMENT_PLAYERS:
            return

        await self.update_tournament_start(tournament)
        await self.remove_offline_players(tournament)

        matches = await self.create_tournament_matches(connected_players)
        await self.channel_layer.group_send(
            self.tournament_group_name,
            {"type": "tournament_message", "message": {"action": "matches_created", "matches": matches}},
        )

    async def tournament_message(self, event: dict) -> None:
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def get_tournament(self) -> Tournament:
        return Tournament.objects.get(id=self.tournament_id)

    @database_sync_to_async
    def get_tournament_players(self) -> list[TournamentPlayer]:
        tournament = Tournament.objects.get(id=self.tournament_id)
        return list(tournament.players.all())

    @database_sync_to_async
    def create_tournament_matches(self, players: list[TournamentPlayer]) -> list[dict]:
        tournament = Tournament.objects.get(id=self.tournament_id)
        random.shuffle(players)
        matches: list[Match] = []
        matches_data: list[dict] = []

        tournament.current_round_number += 1
        tournament.save(update_fields=["current_round_number"])

        if len(players) % 2 != 0:
            bye_player = players.pop()
            tournament_bye = TournamentBye.objects.create(
                player=bye_player, round_number=tournament.current_round_number
            )
            matches_data.append(
                {
                    "player": bye_player.display_name,
                    "is_bye": True,
                    "round": tournament.current_round_number,
                }
            )

        for i in range(0, len(players), 2):
            if i + 1 < len(players):
                match = Match.objects.create(
                    user1=players[i].player, user2=players[i + 1].player, round_number=tournament.current_round_number
                )
                matches.append(match)
                matches_data.append(
                    {
                        "id": str(match.id),
                        "player1": players[i].display_name,
                        "player2": players[i + 1].display_name,
                        "round": tournament.current_round_number,
                    }
                )

        if matches:
            tournament.matches.add(*matches)
        if tournament_bye:
            tournament.byes.add(tournament_bye)

        return matches_data

    @database_sync_to_async
    def get_connected_players(self) -> list[TournamentPlayer]:
        tournament = Tournament.objects.get(id=self.tournament_id)
        connected_users = self.connected_users.get(self.tournament_group_name, set())

        return [player for player in tournament.players.all() if str(player.player.id) in connected_users]

    @database_sync_to_async
    def remove_offline_players(self, tournament: Tournament) -> None:
        connected_users = self.connected_users.get(self.tournament_group_name, set())

        tournament.players.filter(~Q(player__id__in=[UUID(user_id) for user_id in connected_users])).delete()

    @database_sync_to_async
    def update_tournament_start(self, tournament: Tournament) -> None:
        tournament.started_at = now()
        tournament.save(update_fields=["started_at"])

