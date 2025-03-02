import random
import uuid

from django.db import models
from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from apps.users.models import User


class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, related_name="match_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="match_user2", on_delete=models.CASCADE)
    winner = models.ForeignKey(User, related_name="match_winner", null=True, on_delete=models.CASCADE)
    score_user1 = models.PositiveIntegerField(default=0, verbose_name=_("Pontuação do usuário 1"))
    score_user2 = models.PositiveIntegerField(default=0, verbose_name=_("Pontuação do usuário 2"))
    round_number = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Número da rodada"))
    started_date_played = models.DateTimeField(auto_now_add=True, verbose_name=_("Jogado em"))
    finished_date_played = models.DateTimeField(null=True, verbose_name=_("Finalizado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Partida")
        verbose_name_plural = _("Partidas")

    def __str__(self) -> str:
        return f"{self.user1} x {self.user2}"


class TournamentPlayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255, verbose_name=_("Nome de exibição"))
    joined_at = models.DateTimeField(auto_now=True, verbose_name=_("Entrou em"))

    def __str__(self) -> str:
        return self.display_name


class TournamentBye(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    player = models.ForeignKey(TournamentPlayer, on_delete=models.CASCADE)
    round_number = models.PositiveIntegerField(verbose_name=_("Número da rodada"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))

    class Meta:
        verbose_name = _("Bye do Torneio")
        verbose_name_plural = _("Byes do Torneio")

    def __str__(self) -> str:
        return f"{self.player.display_name} - Rodada {self.round_number}"


class Tournament(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Nome do torneio"))
    current_round_number = models.PositiveIntegerField(default=0, verbose_name=_("Número da rodada"))
    players = models.ManyToManyField(TournamentPlayer, related_name="tournament_players")
    matches = models.ManyToManyField(Match, related_name="tournament_matches", blank=True)
    byes = models.ManyToManyField(TournamentBye, related_name="tournament_byes", blank=True)
    winner = models.ForeignKey(
        TournamentPlayer,
        related_name="tournament_winner",
        null=True,
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(User, related_name="tournament_created_by", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    started_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Iniciado em"))
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Finalizado em"))

    class Meta:
        verbose_name = _("Torneio")
        verbose_name_plural = _("Torneios")

    def __str__(self) -> str:
        return self.name

    def check_round_finished(self) -> None:
        if not self.matches.filter(round_number=self.current_round_number, winner__isnull=True).exists():
            self.create_next_round()

    def get_round_winners(self) -> list[TournamentPlayer]:
        winners_ids = self.matches.filter(round_number=self.current_round_number, winner__isnull=False).values_list(
            "winner", flat=True
        )
        bye_players = self.byes.filter(round_number=self.current_round_number).values_list("player", flat=True)

        return list(self.players.filter(Q(player__id__in=winners_ids) | Q(id__in=bye_players)))

    def create_next_round(self) -> None:
        print("create_next_round")
        winners = self.get_round_winners()
        if len(winners) <= 1:
            if winners:
                self.winner = winners[0]
            self.finished_at = now()
            self.save(update_fields=["winner", "finished_at"])
            return []

        random.shuffle(winners)
        matches: list[Match] = []

        self.current_round_number += 1
        self.save(update_fields=["current_round_number"])
        print("current_round_number", self.current_round_number)

        if len(winners) % 2 != 0:
            bye_player = winners.pop()
            tournament_bye = TournamentBye.objects.create(player=bye_player, round_number=self.current_round_number)
            self.byes.add(tournament_bye)

        for i in range(0, len(winners), 2):
            if i + 1 < len(winners):
                print("create_match", winners[i].player, winners[i + 1].player)
                match = Match.objects.create(
                    user1=winners[i].player, user2=winners[i + 1].player, round_number=self.current_round_number
                )
                matches.append(match)

        if matches:
            self.matches.add(*matches)

        return None
