# Generated by Django 5.1.6 on 2025-02-15 22:26

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0006_alter_friendship_status"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Messages",
        ),
    ]
