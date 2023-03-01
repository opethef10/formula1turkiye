from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from fantasy.models import Race, Driver, RaceDriver, Championship

QUESTION_CHOICES = [
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
]


class TahminTeam(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="tahmin_teams")
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE, related_name="tahmin_teams", null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'championship'], name='unique_tahmin_championship_user'),
        ]

    def __str__(self):
        return f"{self.championship.slug} - {self.name()}"

    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_absolute_url(self):
        return reverse("fantasy:team_detail", kwargs={'champ': self.championship.slug, "username": self.user.username})

    def get_tahmin_url(self):
        return reverse("tahmin:team_detail", kwargs={'champ': self.championship.slug, "username": self.user.username})


class RaceTahmin(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='tahmin_team_instances')
    team = models.ForeignKey(TahminTeam, on_delete=models.CASCADE, related_name='race_instances')
    prediction_1 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_1')
    prediction_2 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_2')
    prediction_3 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_3')
    prediction_4 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_4')
    prediction_5 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_5')
    prediction_6 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_6')
    prediction_7 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_7')
    prediction_8 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_8')
    prediction_9 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_9')
    prediction_10 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='prediction_10')
    question_1 = models.CharField(
        max_length=1,
        choices=QUESTION_CHOICES
    )
    question_2 = models.CharField(
        max_length=1,
        choices=QUESTION_CHOICES
    )

    def __str__(self):
        return f"{self.race}-{self.team}"

    def total_point(self):
        return round(sum(getattr(self, f"prediction_{idx}").total_point() for idx in range(1, 11)), 1)  # TODO: Tahmin Puanları
