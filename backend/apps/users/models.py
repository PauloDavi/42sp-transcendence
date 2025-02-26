import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        verbose_name="E-mail",
        max_length=255,
        unique=True,
    )
    avatar = models.ImageField(
        verbose_name=_("Avatar"),
        upload_to="avatars/",
        default="avatars/blank-profile-picture.png",
    )
    status_online = models.BooleanField(default=False)
    wins = models.IntegerField(default=0, verbose_name=_("Vitórias"))
    losses = models.IntegerField(default=0, verbose_name=_("Derrotas"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "password"]

    class Meta:
        verbose_name = _("Usuário")
        verbose_name_plural = _("Usuários")

    def __str__(self):
        return self.username


class FriendshipStatus(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    ACCEPTED = "ACCEPTED", _("Accepted")
    REJECTED = "REJECTED", _("Rejected")


class Friendship(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user1 = models.ForeignKey(
        User, related_name="friendships1", on_delete=models.CASCADE
    )
    user2 = models.ForeignKey(
        User, related_name="friendships2", on_delete=models.CASCADE
    )
    requestd_by = models.ForeignKey(
        User, related_name="friendship_requests", on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=10,
        choices=FriendshipStatus.choices,
        default=FriendshipStatus.PENDING,
        verbose_name=_("Status"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Amizade")
        verbose_name_plural = _("Amizades")
        unique_together = ["user1", "user2"]

    def __str__(self):
        return f"{self.user1.username} e {self.user2.username}"
