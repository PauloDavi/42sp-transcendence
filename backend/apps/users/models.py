import uuid
from django.db import models

# Create your models here.
class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    password = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=50, verbose_name="Nome de Usuário", unique=True)
    avatar = models.ImageField(upload_to="avatars/", default="blank-profile-picture.png")
    status_online = models.BooleanField(default=False)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.name