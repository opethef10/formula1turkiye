# Generated by Django 4.1.4 on 2023-05-17 22:02

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0066_championshipconstructor_alternative_bgcolor_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='championshipconstructor',
            name='alternative_fontcolor',
            field=colorfield.fields.ColorField(default='#000000', image_field=None, max_length=18, samples=None),
        ),
    ]
