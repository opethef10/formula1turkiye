# Generated by Django 4.1 on 2022-12-03 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0019_driver_unique_ref"),
    ]

    operations = [
        migrations.AlterField(
            model_name="driver",
            name="unique_ref",
            field=models.SlugField(null=True, unique=True),
        ),
    ]
