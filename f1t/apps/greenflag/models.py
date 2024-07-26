from django.db import models
from django.urls import reverse

from f1t.apps.fantasy.models import Race
class GreenFlag(models.Model):
    race = models.OneToOneField(Race, on_delete=models.CASCADE, related_name='greenflag_instance')
    title = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return f"{self.race} Green Flag: {self.title}"

    def get_absolute_url(self):
        return reverse('greenflag:greenflag_detail', args=[self.pk])
