# Generated by Django 4.1 on 2022-12-04 15:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("fantasy", "0022_championship_ref_circuit_ref_constructor_ref"),
    ]

    operations = [
        migrations.RenameField(
            model_name="championship",
            old_name="ref",
            new_name="slug",
        ),
        migrations.RenameField(
            model_name="circuit",
            old_name="ref",
            new_name="slug",
        ),
        migrations.RenameField(
            model_name="constructor",
            old_name="ref",
            new_name="slug",
        ),
        migrations.RenameField(
            model_name="driver",
            old_name="ref",
            new_name="slug",
        ),
    ]