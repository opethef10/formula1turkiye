# Generated by Django 4.1 on 2023-02-11 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0050_alter_race_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="race",
            old_name="date",
            new_name="datetime",
        ),
    ]