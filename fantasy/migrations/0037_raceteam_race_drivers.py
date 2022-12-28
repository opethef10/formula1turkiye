# Generated by Django 4.1 on 2022-12-16 19:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0036_championshipconstructor_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="raceteam",
            name="race_drivers",
            field=models.ManyToManyField(
                blank=True, related_name="raceteams", to="fantasy.racedriver"
            ),
        ),
    ]
