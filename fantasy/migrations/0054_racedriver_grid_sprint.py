# Generated by Django 4.1 on 2023-02-12 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0053_alter_race_deadline"),
    ]

    operations = [
        migrations.AddField(
            model_name="racedriver",
            name="grid_sprint",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]