# Generated by Django 5.0.2 on 2024-10-21 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0082_championship_fastest_lap_point_threshold_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='racedriver',
            name='q1',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AddField(
            model_name='racedriver',
            name='q2',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
        migrations.AddField(
            model_name='racedriver',
            name='q3',
            field=models.CharField(blank=True, default='', max_length=10),
        ),
    ]
