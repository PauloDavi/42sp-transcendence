# Generated by Django 5.1.6 on 2025-03-02 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0006_alter_tournament_byes_alter_tournament_finished_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='current_round_number',
            field=models.PositiveIntegerField(default=0, verbose_name='Número da rodada'),
        ),
    ]
