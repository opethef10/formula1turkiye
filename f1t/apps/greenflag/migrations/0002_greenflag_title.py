# Generated by Django 5.0.2 on 2024-07-26 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('greenflag', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='greenflag',
            name='title',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]