# Generated by Django 4.1.4 on 2023-03-05 21:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0056_championship_is_fantasy_championship_is_tahmin"),
        ("tahmin", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Question",
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
                ("text", models.TextField()),
                ("choice_A", models.CharField(max_length=64)),
                ("point_A", models.PositiveSmallIntegerField()),
                ("choice_B", models.CharField(max_length=64)),
                ("point_B", models.PositiveSmallIntegerField()),
                ("choice_C", models.CharField(blank=True, max_length=64, null=True)),
                ("point_C", models.PositiveSmallIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="RaceQuestion",
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
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="question_1_instances",
                        to="tahmin.question",
                    ),
                ),
                (
                    "question_2",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="question_2_instances",
                        to="tahmin.question",
                    ),
                ),
                (
                    "race",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="question_instances",
                        to="fantasy.race",
                    ),
                ),
            ],
        ),
    ]
