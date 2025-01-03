# Generated by Django 5.0.2 on 2024-03-26 11:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ratings', '0002_alter_rating_amount_alter_rating_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='onur',
            field=models.PositiveSmallIntegerField(blank=True, help_text='1 ile 10 arasında değer giriniz.', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)]),
        ),
        migrations.AlterField(
            model_name='rating',
            name='semih',
            field=models.PositiveSmallIntegerField(blank=True, help_text='1 ile 10 arasında değer giriniz.', null=True, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(10)]),
        ),
    ]
