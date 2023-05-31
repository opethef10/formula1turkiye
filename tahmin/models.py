from math import ceil

from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property

from fantasy.models import Race, Driver, RaceDriver, Championship

QUESTION_CHOICES = [
    ("A", "A"),
    ("B", "B"),
    ("C", "C"),
    ("D", "D"),
]


def tahmin_score(count):
    if not 0 < count < 20:
        return 0
    return ceil((20 - count) ** 2 / 2)


class Tahmin(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='tahmins')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tahmins', null=True, blank=True)
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
    answer_1 = models.CharField(
        max_length=1,
        choices=QUESTION_CHOICES
    )
    answer_2 = models.CharField(
        max_length=1,
        choices=QUESTION_CHOICES
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['race', 'user'], name='unique_tahmin'),
        ]
        ordering = [
            "race",
            "user__first_name"
        ]

    def __str__(self):
        return f"{self.race}-{self.user.get_full_name()}"

    @cached_property
    def prediction_point(self):
        questions = self.race.questions.all()[:2]
        result = [None] * 12
        for position in range(1, 11):
            predicted_race_driver = getattr(self, f"prediction_{position}")
            if predicted_race_driver.result == position:
                count = predicted_race_driver.tahmin_count(position)
                point = tahmin_score(count)
                result[position - 1] = point
        for idx in {1, 2}:
            question = questions[idx - 1]
            predicted_answer = getattr(self, f"answer_{idx}")
            if predicted_answer == question.answer:
                result[10 + idx - 1] = question.point
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

    class Meta:
        ordering = ["race"]

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
        return getattr(self, f"point_{self.answer}", 0)
