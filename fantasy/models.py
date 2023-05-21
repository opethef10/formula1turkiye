import json
from decimal import Decimal
from math import ceil
from pathlib import Path

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from django_countries.fields import CountryField
from colorfield.fields import ColorField

TACTIC_CHOICES = [
    ("G", "Geçiş"),
    ("S", "Sıralama"),
    ("F", "Finiş"),
]
CHAMPIONSHIP_CHOICES = [
    ("f1", "Formula 1"),
    ("f2", "Formula 2"),
    ("fe", "Formula E"),
]
OVERTAKE_DOUBLE_POINT_THRESHOLD = 10
DISCOUNT_COEFFICIENTS = (
    Decimal("0.6"),
    Decimal("0.13"),
    Decimal("-0.0044"),
    Decimal("0.000054")
)
JSON_PATH = Path(__file__).parent / "points.json"
with JSON_PATH.open() as json_file:
    POINTS = json.load(
        json_file,
        object_pairs_hook=lambda pairs: {int(k) if k.isnumeric() else k: v for k, v in pairs}
    )


class Championship(models.Model):
    year = models.IntegerField()
    series = models.CharField(
        max_length=255,
        choices=CHAMPIONSHIP_CHOICES
    )
    is_fantasy = models.BooleanField(default=False)
    is_tahmin = models.BooleanField(default=False)
    overtake_coefficient = models.FloatField()
    qualifying_coefficient = models.FloatField()
    finish_coefficient = models.FloatField()
    beginning_token = models.PositiveSmallIntegerField()
    starting_budget = models.DecimalField(max_digits=3, decimal_places=1)
    max_drivers_in_team = models.PositiveSmallIntegerField(default=8)
    price_img = models.FileField(null=True, blank=True)
    slug = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return f"{self.year} {self.get_series_display()} Şampiyonası"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.year}-{self.series}"
        super().save(*args, **kwargs)

    def coefficient(self, tactic):
        if tactic == "G":
            return self.overtake_coefficient
        elif tactic == "S":
            return self.qualifying_coefficient
        elif tactic == "F":
            return self.finish_coefficient

    def latest_race(self):
        try:
            return self.races.filter(
                datetime__lt=timezone.now()
            ).latest("datetime")
        except Race.DoesNotExist:
            return None

    def next_race(self, league):
        try:
            if league == "fantasy":
                return self.races.filter(
                    deadline__gt=timezone.now()
                ).latest("deadline")
            elif league == "tahmin":
                return self.races.filter(
                    datetime__gt=timezone.now(),
                    deadline__lt=timezone.now()
                ).latest("deadline")
        except Race.DoesNotExist:
            return None


class Constructor(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    championship = models.ManyToManyField(Championship, through='ChampionshipConstructor', related_name='constructors')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Driver(models.Model):
    forename = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    number = models.IntegerField(blank=True, null=True)
    code = models.CharField(max_length=3, blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f"{self.forename} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Race(models.Model):
    name = models.CharField(max_length=255)
    championship = models.ForeignKey(Championship, on_delete=models.RESTRICT, related_name='races', null=True)
    round = models.IntegerField()
    country = CountryField()
    datetime = models.DateTimeField()
    deadline = models.DateTimeField(null=True, blank=True)
    wikilink = models.URLField(blank=True)
    drivers = models.ManyToManyField(Driver, through='RaceDriver', related_name='attended_races')
    teams = models.ManyToManyField('Team', through='RaceTeam', related_name='races_involved')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['championship', 'round'], name='unique_championship_round'),
        ]

    def __str__(self):
        return f"{self.championship.year} {self.name}"

    def get_absolute_url(self):
        return reverse("fantasy:race_detail", kwargs={'champ': self.championship.slug, "round": self.round})

    def get_tahmin_url(self):
        return reverse("tahmin:race_detail", kwargs={'champ': self.championship.slug, "round": self.round})

    def next(self):
        try:
            return self.get_next_by_datetime(championship=self.championship)
        except Race.DoesNotExist:
            return None

    def previous(self):
        try:
            return self.get_previous_by_datetime(championship=self.championship)
        except Race.DoesNotExist:
            return None

    @cached_property
    def top10(self):
        top10_drivers = self.driver_instances.filter(
            result__isnull=False
        ).order_by("result")[:10]
        return list(top10_drivers) + [None] * (10 - len(top10_drivers))

    @cached_property
    def tahmin_counts(self):
        return [
            self.tahmin_team_instances.filter(**{f"prediction_{idx}": race_driver}).count()
            for idx, race_driver
            in enumerate(self.top10, 1)
        ]

    @cached_property
    def tahmin_points(self):
        def tahmin_score(count):
            if not 0 < count < 20:
                return 0
            return ceil((20 - count) ** 2 / 2)
        return [tahmin_score(count) for count in self.tahmin_counts]


class RaceDriver(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='driver_instances')
    driver = models.ForeignKey(Driver, on_delete=models.RESTRICT, related_name='race_instances')
    championship_constructor = models.ForeignKey("ChampionshipConstructor", null=True, on_delete=models.SET_NULL, related_name='race_drivers')
    price = models.DecimalField(max_digits=3, decimal_places=1)
    discount = models.BooleanField(default=False)
    qualy = models.PositiveIntegerField(blank=True, null=True)
    grid_sprint = models.PositiveIntegerField(blank=True, null=True)
    sprint = models.PositiveIntegerField(blank=True, null=True)
    sprint_fastest_lap = models.PositiveIntegerField(blank=True, null=True)
    grid = models.PositiveIntegerField(blank=True, null=True)
    result = models.PositiveIntegerField(blank=True, null=True)
    fastest_lap = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['race', 'driver'], name='unique_racedriver'),
        ]

    def __str__(self):
        return f"{self.race}-{self.driver}"

    def qualy_point(self, tactic=None):
        coefficient = self.race.championship.coefficient(tactic) if tactic == "S" else 1
        return round(POINTS["qualy"].get(self.qualy, 0) * coefficient, 1)

    def _sprint_point(self):
        return POINTS["sprint"][self.race.championship.get_series_display()].get(self.sprint, 0)

    def _feature_point(self):
        return POINTS["race"].get(self.result, 0)

    def race_point(self, tactic=None):
        coefficient = self.race.championship.coefficient(tactic) if tactic == "F" else 1
        return round(
            (self._feature_point() + self._sprint_point() + (self.fastest_lap or 0)) * coefficient,
            1
        )

    def _sprint_overtake_point(self):
        if self.race.championship.get_series_display() == "Formula 1":
            return 0
        if not self.grid_sprint or not self.sprint:
            return 0
        elif self.grid_sprint < self.sprint:
            return 0
        else:
            raw = (self.grid_sprint - self.sprint)
            bottom_to_top = max(0, OVERTAKE_DOUBLE_POINT_THRESHOLD - self.sprint)
            top_to_top = max(0, OVERTAKE_DOUBLE_POINT_THRESHOLD - self.grid_sprint)
            return raw + bottom_to_top - top_to_top

    def _feature_overtake_point(self):
        if not self.grid or not self.result:
            return 0
        elif self.grid < self.result:
            return 0
        else:
            raw = (self.grid - self.result)
            bottom_to_top = max(0, OVERTAKE_DOUBLE_POINT_THRESHOLD - self.result)
            top_to_top = max(0, OVERTAKE_DOUBLE_POINT_THRESHOLD - self.grid)
            return raw + bottom_to_top - top_to_top

    def overtake_point(self, tactic=None):
        coefficient = self.race.championship.coefficient(tactic) if tactic == "G" else 1
        return round(
            (self._sprint_overtake_point() + self._feature_overtake_point()) * coefficient,
            1
        )

    def total_point(self, tactic=None):
        return round(self.overtake_point(tactic) + self.qualy_point(tactic) + self.race_point(tactic), 1)

    def discounted_price(self):
        if self.discount:
            discount = sum(
                DISCOUNT_COEFFICIENTS[power] * self.price ** power
                for power
                in range(4)
            )
            return round(self.price - discount, 1)
        return self.price

    def instances(self):
        return self.raceteamdrivers.count()


class Team(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="teams")
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE, related_name="teams", null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'championship'], name='unique_championship_user'),
        ]

    def __str__(self):
        return f"{self.championship.slug} - {self.name()}"

    def name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def get_absolute_url(self):
        return reverse("fantasy:team_detail", kwargs={'champ': self.championship.slug, "username": self.user.username})


class RaceTeam(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='team_instances')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='race_instances')
    token = models.IntegerField()
    budget = models.DecimalField(max_digits=4, decimal_places=1)
    tactic = models.CharField(
        max_length=8,
        choices=TACTIC_CHOICES
    )
    race_drivers = models.ManyToManyField(RaceDriver, through="RaceTeamDriver", related_name='raceteams', blank=True)

    def __str__(self):
        return f"{self.race}-{self.team}"

    @cached_property
    def total_point(self):
        return round(sum(race_driver.total_point(self.tactic) for race_driver in self.race_drivers.all()), 1)

    def overtake_point(self):
        return round(sum(race_driver.total_point("G") for race_driver in self.race_drivers.all()), 1)

    def qualy_point(self):
        return round(sum(race_driver.total_point("S") for race_driver in self.race_drivers.all()), 1)

    def race_point(self):
        return round(sum(race_driver.total_point("F") for race_driver in self.race_drivers.all()), 1)

    def none_point(self):
        return round(sum(race_driver.total_point() for race_driver in self.race_drivers.all()), 1)

    def total_worth(self):
        return round(sum(race_driver.price for race_driver in self.race_drivers.all()) + self.budget, 1)


class RaceTeamDriver(models.Model):
    raceteam = models.ForeignKey(RaceTeam, on_delete=models.CASCADE, related_name='raceteamdrivers')
    racedriver = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='raceteamdrivers')

    def __str__(self):
        return f"{self.raceteam}-{self.racedriver}"

    def total_point(self):
        return self.racedriver.total_point(self.raceteam.tactic)


class ChampionshipConstructor(models.Model):
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE, related_name='constructor_instances')
    constructor = models.ForeignKey(Constructor, on_delete=models.CASCADE, related_name='championship_instances')
    garage_order = models.IntegerField()
    bgcolor = ColorField(default="#f8f9fa")
    alternative_bgcolor = ColorField(default="#f8f9fa")
    fontcolor = ColorField(default="#000000")
    alternative_fontcolor = ColorField(default="#000000")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['championship', 'constructor'], name='unique_championship_constructor'),
            models.UniqueConstraint(fields=['championship', 'garage_order'], name='unique_championship_garage_order'),
        ]

    def __str__(self):
        return f"{self.championship} - {self.constructor}"
