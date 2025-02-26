from django.urls import path
from apps.matchmaking.views import (
    create_match,
    match_game,
    match_refuse,
    create_tournament,
    tournaments,
    delete_tournament,
    join_tournament,
    tournament_detail,
)

urlpatterns = [
    path("game/<uuid:match_id>", match_game, name="match_game"),
    path("create/<uuid:opponent_id>", create_match, name="add_match"),
    path("refuse/<uuid:match_id>", match_refuse, name="match_refuse"),
    path("tournament/create", create_tournament, name="create_tournament"),
    path("tournaments", tournaments, name="tournaments"),
    path(
        "tournament/<uuid:tournament_id>", tournament_detail, name="tournament_detail"
    ),
    path(
        "tournament/<uuid:tournament_id>/delete",
        delete_tournament,
        name="delete_tournament",
    ),
    path(
        "tournament/<uuid:tournament_id>/join", join_tournament, name="join_tournament"
    ),
]
