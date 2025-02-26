import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(
        User, related_name="match_user1", on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        User, related_name="match_user2", on_delete=models.CASCADE
    )
    winner = models.ForeignKey(
        User, related_name="match_winner", null=True, on_delete=models.CASCADE
    )
    score_user1 = models.PositiveIntegerField(
        default=0, verbose_name=_("Pontuação do usuário 1")
    )
    score_user2 = models.PositiveIntegerField(
        default=0, verbose_name=_("Pontuação do usuário 2")
    )
    started_date_played = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Jogado em")
    )
    finished_date_played = models.DateTimeField(
        null=True, verbose_name=_("Finalizado em")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Partida")
        verbose_name_plural = _("Partidas")

    def __str__(self):
        return f"{self.user1} x {self.user2}"


class TournamentPlayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, verbose_name=_("Nome de exibição"))
    joined_at = models.DateTimeField(auto_now=True, verbose_name=_("Entrou em"))

    def __str__(self):
        return self.display_name


class Tournament(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(
        max_length=255, unique=True, verbose_name=_("Nome do torneio")
    )
    players = models.ManyToManyField(
        TournamentPlayer, related_name="tournament_players"
    )
    matches = models.ManyToManyField(Match, related_name="tournament_matches")
    winner = models.ForeignKey(
        TournamentPlayer,
        related_name="tournament_winner",
        null=True,
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        User, related_name="tournament_created_by", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    started_at = models.DateTimeField(null=True, verbose_name=_("Iniciado em"))
    finished_at = models.DateTimeField(null=True, verbose_name=_("Finalizado em"))

    class Meta:
        verbose_name = _("Torneio")
        verbose_name_plural = _("Torneios")

    def __str__(self):
        return self.name
