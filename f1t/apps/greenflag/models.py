from django.db import models
from django.urls import reverse

from f1t.apps.fantasy.models import Race
class GreenFlag(models.Model):
    race = models.OneToOneField(Race, on_delete=models.CASCADE, related_name='greenflag_instance')
    url = models.URLField()

    def __str__(self):
        return f"{self.race} Green Flag Sayısı"

    def get_absolute_url(self):
        return reverse('greenflag:greenflag_detail', args=[self.pk])
