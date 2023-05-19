# Generated by Django 4.1.4 on 2023-05-17 22:02

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0065_championshipconstructor_bgcolor_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='championshipconstructor',
            name='alternative_bgcolor',
            field=colorfield.fields.ColorField(default='#f8f9fa', image_field=None, max_length=18, samples=None),
        ),
        migrations.AddField(
            model_name='championshipconstructor',
            name='alternative_fontcolor',
            field=colorfield.fields.ColorField(default='#f8f9fa', image_field=None, max_length=18, samples=None),
        ),
    ]