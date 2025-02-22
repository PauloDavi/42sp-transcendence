from django.urls import path
from apps.matchmaking.views import create_match, match_game, match_refuse

urlpatterns = [
    path("game/<uuid:match_id>", match_game, name="match_game"),
    path("create/<uuid:opponent_id>", create_match, name="add_match"),
    path("refuse/<uuid:match_id>", match_refuse, name="match_refuse"),
]
