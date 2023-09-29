# Generated by Django 4.1 on 2022-12-04 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0026_alter_championship_slug"),
    ]

    operations = [
        migrations.AlterField(
            model_name="championship",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="circuit",
            name="slug",
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name="constructor",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="driver",
            name="slug",
            field=models.SlugField(editable=False, unique=True),
        ),
    ]