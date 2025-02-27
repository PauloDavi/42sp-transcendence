from django.contrib import admin

from apps.matchmaking.models import Match, Tournament, TournamentPlayer

admin.site.register(Match)
admin.site.register(TournamentPlayer)
admin.site.register(Tournament)
