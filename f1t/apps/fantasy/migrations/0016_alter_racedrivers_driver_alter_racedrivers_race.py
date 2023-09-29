# Generated by Django 4.1 on 2022-11-24 15:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0015_team_race_drivers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="racedrivers",
            name="driver",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="race_instances",
                to="fantasy.driver",
            ),
        ),
        migrations.AlterField(
            model_name="racedrivers",
            name="race",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="driver_instances",
                to="fantasy.race",
            ),
        ),
    ]