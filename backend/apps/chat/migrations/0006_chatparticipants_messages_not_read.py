# Generated by Django 5.1.6 on 2025-03-23 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_blocklist'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatparticipants',
            name='messages_not_read',
            field=models.IntegerField(default=0),
        ),
    ]
