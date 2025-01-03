# Generated by Django 5.0.2 on 2024-02-22 12:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fantasy', '0081_championship_sprint_fastest_lap_point'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('score', models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True)),
                ('onur', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('semih', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('race', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='rating_instance', to='fantasy.race')),
            ],
        ),
    ]
