# Generated by Django 5.0.2 on 2024-02-13 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0080_alter_championshipconstructor_alternative_bgcolor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='championship',
            name='sprint_fastest_lap_point',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
