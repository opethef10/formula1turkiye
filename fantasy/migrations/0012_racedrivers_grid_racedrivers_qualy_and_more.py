# Generated by Django 4.1 on 2022-11-24 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0011_rename_season_championship_team_championship_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="racedrivers",
            name="grid",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="racedrivers",
            name="qualy",
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name="racedrivers",
            name="result",
            field=models.IntegerField(null=True),
        ),
    ]
