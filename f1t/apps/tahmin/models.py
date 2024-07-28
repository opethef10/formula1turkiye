from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property

from ..fantasy.models import Race, Driver, RaceDriver, Championship


class Question(models.Model):
    QUESTION_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]
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
        for char, _ in self.QUESTION_CHOICES:
            choice = getattr(self, f"choice_{char}")
            point = getattr(self, f"point_{char}")
            if choice:
                result += f"\n{char}) {choice} [{point} puan]"
        return result

    @cached_property
    def point(self):
        return getattr(self, f"point_{self.answer}", 0)


class Tahmin(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='tahmins')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tahmins')
    prediction_1 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_1')
    prediction_2 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_2')
    prediction_3 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_3')
    prediction_4 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_4')
    prediction_5 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_5')
    prediction_6 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_6')
    prediction_7 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_7')
    prediction_8 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_8')
    prediction_9 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_9')
    prediction_10 = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='predictions_10')
    answer_1 = models.CharField(
        max_length=1,
        choices=Question.QUESTION_CHOICES
    )
    answer_2 = models.CharField(
        max_length=1,
        choices=Question.QUESTION_CHOICES
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

    def predicted_racedrivers(self):
        for position in range(1, 11):
            yield position, getattr(self, f"prediction_{position}")

    def predicted_answers(self):
        for idx, question in enumerate(self.race.questions.all()[:2], 1):
            yield getattr(self, f"answer_{idx}"), question

    def total_point(self):
        total = 0
        for position, predicted_race_driver in self.predicted_racedrivers():
            total += predicted_race_driver.tahmin_score(position)
        for predicted_answer, question in self.predicted_answers():
            if predicted_answer == question.answer:
                total += question.point
        return total
