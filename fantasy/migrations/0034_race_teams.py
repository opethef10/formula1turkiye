# Generated by Django 4.1 on 2022-12-04 21:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0033_alter_raceteam_race_alter_raceteam_team"),
    ]

    operations = [
        migrations.AddField(
            model_name="race",
            name="teams",
            field=models.ManyToManyField(
                related_name="races_involved",
                through="fantasy.RaceTeam",
                to="fantasy.team",
            ),
        ),
    ]
