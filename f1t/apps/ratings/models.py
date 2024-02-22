from django.db import models

from f1t.apps.fantasy.models import Race


class Rating(models.Model):
    race = models.OneToOneField(Race, on_delete=models.CASCADE, related_name='rating_instance')
    amount = models.PositiveSmallIntegerField(null=True, blank=True)
    score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    onur = models.PositiveSmallIntegerField(null=True, blank=True)
    semih = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.race} Race Rating"
