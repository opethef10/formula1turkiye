# Generated by Django 4.1.4 on 2023-05-26 23:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0069_remove_race_circuit_delete_circuit'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tahmin', '0007_racetahmin_user'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RaceTahmin',
            new_name='Tahmin',
        ),
    ]
