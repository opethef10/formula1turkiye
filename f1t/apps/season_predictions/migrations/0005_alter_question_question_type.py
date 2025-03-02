# Generated by Django 5.1.6 on 2025-03-02 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("season_predictions", "0004_alter_question_positions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="question",
            name="question_type",
            field=models.CharField(
                choices=[
                    ("integer", "Numerical Value"),
                    ("multiple_choice", "Checkbox"),
                    ("single_choice", "Radio Button"),
                    ("text", "Metin"),
                    ("driver_multiselect", "Driver Checkbox"),
                    ("driver_singleselect", "Driver Radio Button"),
                    ("f1_5_driver_multiselect", "Formula 1.5 Driver Checkbox"),
                    ("f1_5_driver_singleselect", "Formula 1.5 Driver Radio Button"),
                    ("race_select", "Race Checkbox"),
                    ("race_singleselect", "Race Radio Button"),
                    ("second_half_race_multiselect", "Second Half Race Checkbox"),
                    ("second_half_race_singleselect", "Second Half Race Radio Button"),
                    ("constructor_singleselect", "Constructor Radio Button"),
                    ("constructor_multiselect", "Constructor Checkbox"),
                    ("boolean", "True/False"),
                    ("driver_matrix", "Driver Matrix"),
                ],
                default="text",
                max_length=32,
                verbose_name="Question Type",
            ),
        ),
    ]
