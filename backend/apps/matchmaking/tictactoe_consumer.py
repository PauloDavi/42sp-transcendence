import asyncio
import json
from dataclasses import dataclass
from typing import ClassVar

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now

from apps.matchmaking.models import Match


@dataclass
class Player:
    username: str | None
    is_online: bool

    def __init__(self) -> None:
        self.username = None
        self.is_online = False

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "is_online": self.is_online,
        }

@dataclass
class Players:
    player_x: Player
    player_o: Player

    def __init__(self) -> None:
        self.player_x = Player()
        self.player_o = Player()

    def to_dict(self) -> dict:
        return {
            "player_x": self.player_x.to_dict(),
            "player_o": self.player_o.to_dict(),
        }

@dataclass
class GameObject:
    board: list[str]
    turn: str
    winner: str | None
    players: Players

    def __init__(self) -> None:
        self.board = ["" for _ in range(25)]
        self.players = Players()
        self.turn = "X"
        self.winner = None

    def to_dict(self) -> dict:
        return {
            "board": self.board,
            "turn": self.turn,
            "winner": self.winner,
            "players": self.players.to_dict(),
        }


class TicTacToeConsumer(AsyncWebsocketConsumer):
    games: ClassVar[dict[str, GameObject]] = {}
    locks: ClassVar[dict] = {}
    winning_combinations: ClassVar[list[tuple[int]]] = [
            (0, 1, 2, 3, 4), (0, 1, 2, 3), (1, 2, 3, 4),
            (5, 6, 7, 8, 9), (5, 6, 7, 8), (6, 7, 8, 9),
            (10, 11, 12, 13, 14), (10, 11, 12, 13), (11, 12, 13, 14),
            (15, 16, 17, 18, 19), (15, 16, 17, 18), (16, 17, 18, 19),
            (20, 21, 22, 23, 24), (20, 21, 22, 23), (21, 22, 23, 24),

            (0, 5, 10, 15, 20), (0, 5, 10, 15), (5, 10, 15, 20),
            (1, 6, 11, 16, 21), (1, 6, 11, 16), (6, 11, 16, 21),
            (2, 7, 12, 17, 22), (2, 7, 12, 17), (7, 12, 17, 22),
            (3, 8, 13, 18, 23), (3, 8, 13, 18), (8, 13, 18, 23),
            (4, 9, 14, 19, 24), (4, 9, 14, 19), (9, 14, 19, 24),

            (0, 6, 12, 18, 24), (4, 8, 12, 16, 20),
            (0, 6, 12, 18), (6, 12, 18, 24),
            (1, 7, 13, 19), (5, 11, 17, 23),
            (4, 8, 12, 16), (8, 12, 16, 20),
            (3, 7, 11, 15), (9, 13, 17, 21),
        ]

    async def connect(self) -> None:
        self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
        self.room_group_name = f"match_{self.match_id}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.match = await database_sync_to_async(Match.objects.get)(id=self.match_id)
        if self.match.finished_date_played or not await self.is_user_in_match():
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.room_group_name not in self.games:
            self.games[self.room_group_name] = GameObject()
            self.locks[self.room_group_name] = asyncio.Lock()

        game = self.games[self.room_group_name]
        if game.players.player_x.username is None:
            game.players.player_x.username = self.user.username
            game.players.player_x.is_online = True
            self.player = "X"
        else:
            game.players.player_o.username = self.user.username
            game.players.player_o.is_online = True
            self.player = "O"

        if game.players.player_x.is_online and game.players.player_o.is_online:
            await self.send_game_state([{ "type": "start_game" }])

    async def disconnect(self, close_code: int) -> None:
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        game = self.games.get(self.room_group_name)
        if game is None:
            return

        if game.players.player_x.username == self.user.username:
            game.players.player_x.is_online = False
        else:
            game.players.player_o.is_online = False

        if game.players.player_x.is_online is False and game.players.player_o.is_online is False:
            if not self.match.finished_date_played:
                self.match.winner = self.user
                self.match.finished_date_played = now()
                await self.match.asave(update_fields=["winner", "finished_date_played"])

            del self.games[self.room_group_name]
            del self.locks[self.room_group_name]

    async def receive(self, text_data: str) -> None:
        data = json.loads(text_data)
        action = data.get("action")
        position = data.get("position")

        if action == "click" and position is not None:
            await self.player_click(position)

    async def player_click(self, position: int) -> None:
        async with self.locks[self.room_group_name]:
            game = self.games[self.room_group_name]
            if game.winner or game.board[position] != "" or game.turn != self.player:
                return

            game.board[position] = self.player
            game.turn = "X" if self.player == "O" else "O"

            game.winner = self.check_winner(game.board)
            await self.send_game_state([
                { "type": "put_symbol", "position": position, "symbol": self.player },
                { "type": "finish_game", "winner": game.winner } if game.winner else None,
            ])

    def check_winner(self, board: list[str]) -> str | None:
        for combination in self.winning_combinations:
            a, b, c, d, f = combination
            if board[a] and board[a] == board[b] == board[c] == board[d] and  (board[a] == board[f] if f else True):
                return board[a]
        return None

    async def send_game_state(self, events: list[dict | None]) -> None:
        game = self.games.get(self.room_group_name)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_state",
                "game": game.to_dict(),
                "events": [event for event in events if event is not None],
            },
        )

    async def game_state(self, event: dict) -> None:
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def is_user_in_match(self) -> bool:
        return self.user in (self.match.user1, self.match.user2)
