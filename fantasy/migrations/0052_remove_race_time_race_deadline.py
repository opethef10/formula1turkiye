# Generated by Django 4.1 on 2023-02-11 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0051_rename_date_race_datetime"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="race",
            name="time",
        ),
        migrations.AddField(
            model_name="race",
            name="deadline",
            field=models.DateTimeField(null=True),
        ),
    ]
