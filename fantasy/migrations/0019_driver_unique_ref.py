# Generated by Django 4.1 on 2022-12-03 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0018_racedrivers_fastest_lap_racedrivers_sprint"),
    ]

    operations = [
        migrations.AddField(
            model_name="driver",
            name="unique_ref",
            field=models.SlugField(null=True),
        ),
    ]