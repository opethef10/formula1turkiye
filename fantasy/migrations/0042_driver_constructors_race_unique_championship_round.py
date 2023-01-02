# Generated by Django 4.1 on 2023-01-02 13:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0041_raceteamdriver_alter_raceteam_race_drivers_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="driver",
            name="constructors",
            field=models.ManyToManyField(
                null=True, related_name="drivers", to="fantasy.championshipconstructor"
            ),
        ),
        migrations.AddConstraint(
            model_name="race",
            constraint=models.UniqueConstraint(
                fields=("championship", "round"), name="unique_championship_round"
            ),
        ),
    ]
