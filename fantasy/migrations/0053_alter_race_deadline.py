# Generated by Django 4.1 on 2023-02-11 12:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0052_remove_race_time_race_deadline"),
    ]

    operations = [
        migrations.AlterField(
            model_name="race",
            name="deadline",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
