# Generated by Django 4.1 on 2022-12-04 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0027_alter_championship_slug_alter_circuit_slug_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="circuit",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
    ]
