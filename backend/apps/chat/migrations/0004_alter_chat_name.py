# Generated by Django 5.1.6 on 2025-02-26 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_message_delete_messages'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
