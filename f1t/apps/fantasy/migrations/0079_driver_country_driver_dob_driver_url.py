# Generated by Django 4.1.4 on 2023-11-11 17:55

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0078_alter_constructor_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='country',
            field=django_countries.fields.CountryField(blank=True, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='dob',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='driver',
            name='url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
