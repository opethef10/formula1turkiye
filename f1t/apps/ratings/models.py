from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from f1t.apps.fantasy.models import Race

HELP_TEXT = "1 ile 10 arasında değer giriniz ya da boş bırakınız."
VALIDATORS=[
    MinValueValidator(1),
    MaxValueValidator(10)
]

class Rating(models.Model):
    race = models.OneToOneField(Race, on_delete=models.CASCADE, related_name='rating_instance')
    amount = models.PositiveSmallIntegerField()
    score = models.DecimalField(max_digits=4, decimal_places=2)
    onur = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=VALIDATORS,
        help_text=HELP_TEXT
    )
    semih = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=VALIDATORS,
        help_text=HELP_TEXT
    )

    def __str__(self):
        return f"{self.race} Race Rating"

