# Generated by Django 4.1 on 2022-11-24 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0009_delete_series_season_series"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="race",
            name="year",
        ),
        migrations.AddField(
            model_name="race",
            name="championship",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="races",
                to="fantasy.season",
            ),
        ),
    ]