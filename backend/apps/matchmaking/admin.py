from django.contrib import admin

from apps.matchmaking.models import Match, Tournament, TournamentBye, TournamentPlayer


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at", "started_at", "finished_at", "winner")
    readonly_fields = ("created_at", "winner", "players")
    filter_horizontal = ("players", "matches", "byes")


admin.site.register(Match)
admin.site.register(TournamentPlayer)
admin.site.register(TournamentBye)
