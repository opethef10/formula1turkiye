# Generated by Django 4.1.4 on 2023-08-24 12:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tahmin', '0011_alter_question_options_alter_tahmin_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tahmin',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tahmins', to=settings.AUTH_USER_MODEL),
        ),
    ]