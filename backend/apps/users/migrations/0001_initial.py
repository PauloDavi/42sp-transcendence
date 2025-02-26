# Generated by Django 5.1.6 on 2025-02-07 11:24

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("password", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254, unique=True)),
                (
                    "user_name",
                    models.CharField(max_length=50, unique=True, verbose_name="Nome de Usuário"),
                ),
                (
                    "avatar",
                    models.ImageField(default="blank-profile-picture.png", upload_to="avatars/"),
                ),
                ("status_online", models.BooleanField(default=False)),
                ("wins", models.IntegerField(default=0)),
                ("losses", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Usuário",
                "verbose_name_plural": "Usuários",
            },
        ),
    ]
