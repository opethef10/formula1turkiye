# Generated by Django 4.1.4 on 2023-11-10 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0075_circuit_race_circuit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='raceteam',
            options={'ordering': ['race', 'user']},
        ),
        migrations.AlterModelOptions(
            name='raceteamdriver',
            options={'ordering': ['racedriver__race', 'raceteam__user__first_name', '-racedriver__price']},
        ),
        migrations.RemoveField(
            model_name='race',
            name='teams',
        ),
        migrations.RemoveField(
            model_name='raceteam',
            name='team',
        ),
        migrations.DeleteModel(
            name='Team',
        ),
    ]
