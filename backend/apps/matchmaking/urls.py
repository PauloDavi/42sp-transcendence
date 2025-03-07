from django.urls import path

from apps.matchmaking.views import (
    create_ai_match,
    create_match,
    create_tournament,
    delete_tournament,
    join_tournament,
    leave_tournament,
    match_game,
    match_refuse,
    tournament_room,
    tournaments,
)

urlpatterns = [
    path("game/<uuid:match_id>", match_game, name="match_game"),
    path("create/<uuid:opponent_id>", create_match, name="add_match"),
    path("refuse/<uuid:match_id>", match_refuse, name="match_refuse"),
    path("tournament/create", create_tournament, name="create_tournament"),
    path("tournaments", tournaments, name="tournaments"),
    path("tournament/<uuid:tournament_id>", tournament_room, name="tournament_room"),
    path(
        "tournament/<uuid:tournament_id>/delete",
        delete_tournament,
        name="delete_tournament",
    ),
    path("tournament/<uuid:tournament_id>/join", join_tournament, name="join_tournament"),
    path("tournament/<uuid:tournament_id>/leave/", leave_tournament, name="leave_tournament"),
    path("create-ai-match/", create_ai_match, name="create_ai_match"),
]
