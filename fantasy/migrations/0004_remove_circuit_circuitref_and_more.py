# Generated by Django 4.1 on 2022-11-22 18:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0003_alter_race_drivers"),
    ]

    operations = [
        migrations.RemoveField(model_name="circuit", name="circuitref",),
        migrations.RemoveField(model_name="constructor", name="constructorref",),
        migrations.RemoveField(model_name="driver", name="driverref",),
    ]
