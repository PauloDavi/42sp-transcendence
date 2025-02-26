import asyncio
import json
import secrets
import time
from typing import ClassVar

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils.timezone import now

from apps.matchmaking.models import Match
from apps.users.models import User

# Configurações do jogo
GRID_WIDTH = 50
GRID_HEIGHT = 25
PADDLE_HEIGHT = 5.0
PADDLE_WIDTH = 1.0
BALL_SIZE = 1.0
BALL_SPEED = 0.4
PADDLE_X_OFFSET = 2.0
FRAME_DELAY = 1 / 30
PADDLE_SPEED = 0.3
WIN_SCORE = 3
REQUIRED_NUMBER_OF_PLAYERS = 2


class PongConsumer(AsyncWebsocketConsumer):
    games: ClassVar[dict] = {}
    game_locks: ClassVar[dict] = {}

    async def connect(self) -> None:
        self.match_id = self.scope["url_route"]["kwargs"]["match_id"]
        self.room_group_name = f"match_{self.match_id}"
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close()
            return

        self.match = await database_sync_to_async(Match.objects.get)(id=self.match_id)

        if self.match.finished_date_played:
            await self.close()
            return

        if not await verify_if_user_in_match(self.match, self.user):
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        if self.room_group_name not in self.games:
            self.games[self.room_group_name] = {
                "players": {},
                "paddles": {
                    "left_paddle": {
                        "y": GRID_HEIGHT / 2 - PADDLE_HEIGHT / 2,
                        "x": PADDLE_X_OFFSET,
                        "vy": 0,
                        "width": PADDLE_WIDTH,
                        "height": PADDLE_HEIGHT,
                    },
                    "right_paddle": {
                        "y": GRID_HEIGHT / 2 - PADDLE_HEIGHT / 2,
                        "x": GRID_WIDTH - PADDLE_X_OFFSET - PADDLE_WIDTH,
                        "vy": 0,
                        "width": PADDLE_WIDTH,
                        "height": PADDLE_HEIGHT,
                    },
                },
                "ball": {
                    "x": GRID_WIDTH / 2 - BALL_SIZE / 2,
                    "y": GRID_HEIGHT / 2 - BALL_SIZE / 2,
                    "vx": BALL_SPEED,
                    "vy": BALL_SPEED,
                    "width": BALL_SIZE,
                    "height": BALL_SIZE,
                    "resseting": False,
                    "reset_timer": 0,
                },
                "score": {"left_score": 0, "right_score": 0},
                "running": False,
            }
            self.game_locks[self.room_group_name] = asyncio.Lock()

        self.is_left_user = await is_left_user(self.match, self.user)

        game = self.games[self.room_group_name]
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "send_game_state", "game": game, "events": []},
        )

        if self.user.username not in game["players"]:
            game["players"][self.user.username] = self.channel_name

        if len(game["players"].values()) == REQUIRED_NUMBER_OF_PLAYERS and not game["running"]:
            game["running"] = True
            if not hasattr(self, "game_task") or self.game_task.done():
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_game_state",
                        "game": game,
                        "events": [{"type": "game_start"}],
                    },
                )
                self.game_task = asyncio.create_task(self.game_loop())

    async def disconnect(self, message: dict) -> None:
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        game = self.games.get(self.room_group_name)
        if not game:
            return

        for username, channel in game["players"].items():
            if channel == self.channel_name:
                game["players"][username] = None

        if all(p is None for p in game["players"].values()):
            del self.games[self.room_group_name]
            self.match.score_user1 = game["score"]["left_score"]
            self.match.score_user2 = game["score"]["right_score"]
            self.match.finished_date_played = now()
            await self.match.asave(update_fields=["score_user1", "score_user2", "finished_date_played"])

            if game["score"]["left_score"] == game["score"]["right_score"]:
                return

            winner = (
                self.match.user1 if game["score"]["left_score"] > game["score"]["right_score"] else self.match.user2
            )
            losser = (
                self.match.user2 if game["score"]["left_score"] > game["score"]["right_score"] else self.match.user1
            )
            winner.wins += 1
            losser.losses += 1
            self.match.winner = winner
            await self.match.asave(update_fields=["winner"])
            await winner.asave(update_fields=["wins"])
            await losser.asave(update_fields=["losses"])

    async def receive(self, text_data: str) -> None:
        data = json.loads(text_data)
        game = self.games.get(self.room_group_name)
        if not game:
            return

        async with self.game_locks[self.room_group_name]:
            paddles = game["paddles"]
            paddle_key = "left_paddle" if self.is_left_user else "right_paddle"
            speed = PADDLE_SPEED if data["event"] == "keydown" else 0
            if data["type"] == "up":
                paddles[paddle_key]["vy"] = -speed
            elif data["type"] == "down":
                paddles[paddle_key]["vy"] = speed

    async def game_loop(self) -> None:
        while self.room_group_name in self.games and self.games[self.room_group_name]["running"]:
            start_time = time.perf_counter()
            await self.update_game_state()
            elapsed_time = time.perf_counter() - start_time
            sleep_time = max(FRAME_DELAY - elapsed_time, 0)
            await asyncio.sleep(sleep_time)

    async def update_game_state(self) -> None:
        game = self.games.get(self.room_group_name)
        if not game:
            return

        ball = game["ball"]
        paddles = game["paddles"]
        events = []

        async with self.game_locks[self.room_group_name]:
            await self.update_ball_position(ball)
            await self.update_paddle_positions(paddles)
            await self.check_wall_collisions(ball, events)
            await self.check_paddle_collisions(ball, paddles, events)
            await self.check_score(ball, game, events)

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "send_game_state", "game": game, "events": events},
        )

    async def update_ball_position(self, ball: dict) -> None:
        if not ball["resseting"]:
            ball["x"] += ball["vx"]
            ball["y"] += ball["vy"]
        elif time.perf_counter() > ball["reset_timer"]:
            ball["resseting"] = False

    async def update_paddle_positions(self, paddles: dict) -> None:
        paddles["left_paddle"]["y"] = max(
            1.0,
            min(
                GRID_HEIGHT - PADDLE_HEIGHT - 1.0,
                paddles["left_paddle"]["y"] + paddles["left_paddle"]["vy"],
            ),
        )
        paddles["right_paddle"]["y"] = max(
            1.0,
            min(
                GRID_HEIGHT - PADDLE_HEIGHT - 1.0,
                paddles["right_paddle"]["y"] + paddles["right_paddle"]["vy"],
            ),
        )

    async def check_wall_collisions(self, ball: dict, events: list) -> None:
        if ball["y"] < 1.0 or ball["y"] > GRID_HEIGHT - 2.0:
            ball["vy"] *= -1
            events.append({"type": "wall_hit"})

    async def check_paddle_collisions(self, ball: dict, paddles: dict, events: list) -> None:
        left_paddle = paddles["left_paddle"]
        right_paddle = paddles["right_paddle"]

        def update_ball_when_collide_with_paddle(paddle: dict, new_ball_x: int) -> None:
            impact_point = ball["y"] + ball["height"] / 2 - (paddle["y"] + paddle["height"] / 2)
            normalized_impact = impact_point / (paddle["height"] / 2)
            ball["vx"] *= -1.05
            ball["vy"] = normalized_impact * BALL_SPEED
            ball["x"] = new_ball_x

        if (
            left_paddle["x"] < ball["x"] < left_paddle["x"] + left_paddle["width"]
            and (left_paddle["y"] - ball["height"]) < ball["y"] < left_paddle["y"] + left_paddle["height"]
        ):
            update_ball_when_collide_with_paddle(left_paddle, left_paddle["x"] + left_paddle["width"])
            events.append({"type": "paddle_hit"})

        if (
            right_paddle["x"] < (ball["x"] + BALL_SIZE) < right_paddle["x"] + right_paddle["width"]
            and (right_paddle["y"] - ball["height"]) < ball["y"] < right_paddle["y"] + right_paddle["height"]
        ):
            update_ball_when_collide_with_paddle(right_paddle, right_paddle["x"] - ball["width"])
            events.append({"type": "paddle_hit"})

    async def check_score(self, ball: dict, game: dict, events: list) -> None:
        if ball["x"] < 0.0 or ball["x"] > GRID_WIDTH - BALL_SIZE:
            scoring_player = "right_score" if ball["x"] < 0.0 else "left_score"
            game["score"][scoring_player] += 1
            events.append({"type": "score_update"})

            game["ball"] = {
                "x": GRID_WIDTH / 2 - BALL_SIZE / 2,
                "y": GRID_HEIGHT / 2 - BALL_SIZE / 2,
                "vx": (1 if secrets.randbelow(2) == 1 else -1) * BALL_SPEED,
                "vy": (1 if secrets.randbelow(2) == 1 else -1) * BALL_SPEED * secrets.SystemRandom().uniform(0.5, 1.5),
                "width": BALL_SIZE,
                "height": BALL_SIZE,
                "resseting": True,
                "reset_timer": time.perf_counter() + secrets.SystemRandom().uniform(0.5, 1.5),
            }

            if game["score"][scoring_player] >= WIN_SCORE:
                winner = self.match.user1 if scoring_player == "left_score" else self.match.user2
                losser = self.match.user2 if scoring_player == "left_score" else self.match.user1
                asyncio.create_task(self.update_match_winner(self.match, winner, losser, game["score"]))  # noqa: RUF006
                game["running"] = False
                events.append({"type": "game_over", "winner": winner.username})

    async def update_match_winner(self, match: Match, winner: User, losser: User, scores: dict) -> None:
        match.winner = winner
        match.score_user1 = scores["left_score"]
        match.score_user2 = scores["right_score"]
        match.finished_date_played = now()
        await match.asave(update_fields=["winner", "score_user1", "score_user2", "finished_date_played"])

        winner.wins += 1
        losser.losses += 1
        await winner.asave(update_fields=["wins"])
        await losser.asave(update_fields=["losses"])

    async def send_game_state(self, event: dict) -> None:
        await self.send(text_data=json.dumps({"game": event["game"], "events": event["events"]}))


@database_sync_to_async
def is_left_user(match: Match, user: User) -> bool:
    return user == match.user1


@database_sync_to_async
def verify_if_user_in_match(match: Match, user: User) -> bool:
    return user in {match.user1, match.user2}
