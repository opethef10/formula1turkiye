# Generated by Django 4.1.4 on 2023-05-31 19:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tahmin', '0009_remove_tahmin_team_alter_tahmin_race_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tahmin',
            old_name='question_1',
            new_name='answer_1',
        ),
        migrations.RenameField(
            model_name='tahmin',
            old_name='question_2',
            new_name='answer_2',
        ),
    ]