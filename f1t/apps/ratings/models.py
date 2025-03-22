from math import sqrt, ceil, floor

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from f1t.apps.fantasy.models import Race

HELP_TEXT = "1 ile 10 arasında değer giriniz ya da boş bırakınız."
VOTE_COUNT_VALIDATORS = [
    MinValueValidator(0)
]
VALIDATORS = [
    MinValueValidator(1),
    MaxValueValidator(10)
]


class Rating(models.Model):
    MIN_SCORE = 1
    MAX_SCORE = 10
    SIGMA = 2
    ROUND_DIGITS = 2
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
    vote_count_1 = models.PositiveIntegerField(default=0, verbose_name="1", validators=VOTE_COUNT_VALIDATORS)
    vote_count_2 = models.PositiveIntegerField(default=0, verbose_name="2", validators=VOTE_COUNT_VALIDATORS)
    vote_count_3 = models.PositiveIntegerField(default=0, verbose_name="3", validators=VOTE_COUNT_VALIDATORS)
    vote_count_4 = models.PositiveIntegerField(default=0, verbose_name="4", validators=VOTE_COUNT_VALIDATORS)
    vote_count_5 = models.PositiveIntegerField(default=0, verbose_name="5", validators=VOTE_COUNT_VALIDATORS)
    vote_count_6 = models.PositiveIntegerField(default=0, verbose_name="6", validators=VOTE_COUNT_VALIDATORS)
    vote_count_7 = models.PositiveIntegerField(default=0, verbose_name="7", validators=VOTE_COUNT_VALIDATORS)
    vote_count_8 = models.PositiveIntegerField(default=0, verbose_name="8", validators=VOTE_COUNT_VALIDATORS)
    vote_count_9 = models.PositiveIntegerField(default=0, verbose_name="9", validators=VOTE_COUNT_VALIDATORS)
    vote_count_10 = models.PositiveIntegerField(default=0, verbose_name="10", validators=VOTE_COUNT_VALIDATORS)


    def __str__(self):
        return f"{self.race} Race Rating"


    def get_vote_counts(self):
        return [getattr(self, f'vote_count_{score}', 0) for score in range(self.MIN_SCORE, self.MAX_SCORE + 1)]

    def total(self):
        return sum(self.get_vote_counts())

    def score_(self):
        vote_counts = self.get_vote_counts()
        total_votes = sum(vote_counts)

        if total_votes <= 0:
            return None

        mean = sum(
            score * count
            for score, count
            in enumerate(vote_counts, start=self.MIN_SCORE)
        ) / total_votes
        sum_of_squares = sum(
            ((score - mean) ** 2) * count
            for score, count
            in enumerate(vote_counts, start=self.MIN_SCORE)
        )
        variance = sum_of_squares / total_votes
        standard_deviation = sqrt(variance)

        lower_threshold = max(self.MIN_SCORE, ceil(mean - self.SIGMA * standard_deviation))
        upper_threshold = min(self.MAX_SCORE, floor(mean + self.SIGMA * standard_deviation))

        accepted_vote_counts = vote_counts[lower_threshold - 1: upper_threshold]
        accepted_total_votes = sum(accepted_vote_counts)
        race_score = sum(
            score * count
            for score, count
            in enumerate(accepted_vote_counts, start=lower_threshold)
        ) / accepted_total_votes

        return round(race_score, self.ROUND_DIGITS)
