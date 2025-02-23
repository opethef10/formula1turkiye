from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from f1t.apps.fantasy.models import Championship


class Question(models.Model):
    QUESTION_TYPES = [
        ('integer', 'Numerical Value'),
        ('multiple_choice', 'Checkbox'),
        ('single_choice', 'Radio Button'),
        ('text', 'Metin'),
        ('driver_multiselect', 'Driver Checkbox'),
        ('driver_singleselect', 'Driver Radio Button'),
        ('race_singleselect', 'Race Radio Button'),
        ('race_select', 'Race Checkbox'),
        ('constructor_singleselect', 'Constructor Radio Button'),
        ('constructor_multiselect', 'Constructor Checkbox'),
        ('boolean', 'True/False'),
        ('driver_matrix', 'Driver Matrix'),
    ]

    championship = models.ForeignKey(Championship, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(verbose_name="Question Number")
    text = models.TextField(verbose_name="Question Text")
    help_text = models.TextField(blank=True, verbose_name="Help Text")
    question_type = models.CharField(
        max_length=32,
        choices=QUESTION_TYPES,
        default='text',
        verbose_name="Question Type"
    )
    positions = models.PositiveIntegerField(
        default=0,
        verbose_name="Matrix Positions",
        help_text="Number of positions in the ranking matrix (only for driver matrix questions)"
    )
    choices = models.TextField(
        blank=True,
        help_text="Comma-separated list of choices for multiple choice questions",
        verbose_name="Choices"
    )
    active = models.BooleanField(default=True, verbose_name="Active")
    validation_min = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Minimum Value"
    )
    validation_max = models.IntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(1000)],
        verbose_name="Maximum Value"
    )

    class Meta:
        ordering = ['order']
        verbose_name = "Question"
        verbose_name_plural = "Questions"

    def __str__(self):
        return f"{self.order}. {self.text[:50]}"


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'championship'],
                name='unique_user_championship'
            )
        ]


class Answer(models.Model):
    prediction = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    value = models.JSONField()

    class Meta:
        unique_together = ['prediction', 'question']
