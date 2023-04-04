from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property

from fantasy.models import Race, Driver, RaceDriver, Championship

QUESTION_CHOICES = [
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
    ("D", "D"),
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

    @cached_property
    def prediction_point(self):
        top10 = self.race.top10
        points = self.race.tahmin_points
        questions = self.race.questions.all()[:2]
        result = []
        for position in range(1, 11):
            predicted_driver = getattr(self, f"prediction_{position}")
            resulting_racedriver = top10[position-1]
            position_point = points[position-1]
            if predicted_driver == resulting_racedriver:
                result.append(position_point)
            else:
                result.append(None)
        for idx in {1, 2}:
            predicted_answer = getattr(self, f"question_{idx}")
            actual_answer = questions[idx-1].answer
            question_point = questions[idx-1].point
            if predicted_answer == actual_answer:
                result.append(question_point)
            else:
                result.append(None)
        return result

    def total_point(self):
        return round(sum(point for point in self.prediction_point if point is not None), 1)


class Question(models.Model):
    race = models.ForeignKey(Race, on_delete=models.RESTRICT, related_name='questions', null=True)
    text = models.TextField()
    choice_A = models.CharField(max_length=64)
    point_A = models.PositiveSmallIntegerField()
    choice_B = models.CharField(max_length=64)
    point_B = models.PositiveSmallIntegerField()
    choice_C = models.CharField(null=True, blank=True, max_length=64)
    point_C = models.PositiveSmallIntegerField(null=True, blank=True)
    choice_D = models.CharField(null=True, blank=True, max_length=64)
    point_D = models.PositiveSmallIntegerField(null=True, blank=True)
    answer = models.CharField(
        max_length=1,
        choices=QUESTION_CHOICES,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.race} - {self.form_str()}"

    def form_str(self):
        result = f"{self.text}\n"
        for char, _ in QUESTION_CHOICES:
            choice = getattr(self, f"choice_{char}")
            point = getattr(self, f"point_{char}")
            if choice:
                result += f"\n{char}) {choice} [{point} puan]"
        return result

    @cached_property
    def point(self):
        return getattr(self, f"point_{self.answer}")
