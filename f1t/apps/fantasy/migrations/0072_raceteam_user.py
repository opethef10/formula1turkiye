# Generated by Django 4.1.4 on 2023-08-24 12:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fantasy', '0071_alter_championship_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='raceteam',
            name='user',
            field=models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, related_name='fantasy_instances', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
