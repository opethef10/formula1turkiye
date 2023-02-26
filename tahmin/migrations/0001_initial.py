# Generated by Django 4.1.4 on 2023-02-23 11:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("fantasy", "0056_championship_is_fantasy_championship_is_tahmin"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TahminTeam",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "championship",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tahmin_teams",
                        to="fantasy.championship",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tahmin_teams",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="RaceTahmin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "question_1",
                    models.CharField(
                        choices=[("A", "A"), ("B", "B"), ("C", "C")], max_length=1
                    ),
                ),
                (
                    "question_2",
                    models.CharField(
                        choices=[("A", "A"), ("B", "B"), ("C", "C")], max_length=1
                    ),
                ),
                (
                    "prediction_1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_1",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_10",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_10",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_2",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_3",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_3",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_4",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_4",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_5",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_5",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_6",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_6",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_7",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_7",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_8",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_8",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "prediction_9",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prediction_9",
                        to="fantasy.racedriver",
                    ),
                ),
                (
                    "race",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tahmin_team_instances",
                        to="fantasy.race",
                    ),
                ),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="race_instances",
                        to="tahmin.tahminteam",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="tahminteam",
            constraint=models.UniqueConstraint(
                fields=("user", "championship"), name="unique_tahmin_championship_user"
            ),
        ),
    ]
