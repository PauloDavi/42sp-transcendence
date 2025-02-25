from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from apps.users.models import User

class Match(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(User, related_name="match_user1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="match_user2", on_delete=models.CASCADE)
    winner = models.ForeignKey(User, related_name="match_winner", null=True, on_delete=models.CASCADE)
    score_user1 = models.PositiveIntegerField(default=0, verbose_name=_("Pontuação do usuário 1"))
    score_user2 = models.PositiveIntegerField(default=0, verbose_name=_("Pontuação do usuário 2"))
    started_date_played = models.DateTimeField(auto_now_add=True, verbose_name=_("Jogado em"))
    finished_date_played = models.DateTimeField(null=True, verbose_name=_("Finalizado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Partida")
        verbose_name_plural = _("Partidas")

    def __str__(self):
        return f"{self.user1} x {self.user2}"
