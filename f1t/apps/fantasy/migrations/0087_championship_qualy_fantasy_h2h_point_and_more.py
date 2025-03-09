# Generated by Django 5.1.6 on 2025-03-09 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0086_championship_pole_point"),
    ]

    operations = [
        migrations.AddField(
            model_name="championship",
            name="qualy_fantasy_h2h_point",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="championship",
            name="race_fantasy_h2h_point",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
