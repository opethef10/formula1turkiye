# Generated by Django 4.1.4 on 2023-11-11 13:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0077_constructor_country_constructor_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='constructor',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
