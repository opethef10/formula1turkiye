# Generated by Django 4.1.4 on 2023-03-29 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0060_championship_finish_coefficient_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='championship',
            name='beginning_token',
            field=models.PositiveSmallIntegerField(default=18),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='championship',
            name='max_drivers_in_team',
            field=models.PositiveSmallIntegerField(default=8),
        ),
        migrations.AddField(
            model_name='championship',
            name='starting_budget',
            field=models.DecimalField(decimal_places=1, default=50.0, max_digits=3),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='championship',
            name='is_fantasy',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='championship',
            name='is_tahmin',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='championship',
            name='series',
            field=models.CharField(choices=[('f1', 'Formula 1'), ('f2', 'Formula 2'), ('fe', 'Formula E')], max_length=255),
        ),
    ]
