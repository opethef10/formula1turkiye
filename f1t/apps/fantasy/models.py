import json
from decimal import Decimal
from functools import cache
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

JSON_PATH = Path(__file__).parent / "points.json"
with JSON_PATH.open() as json_file:
    POINTS = json.load(
        json_file,
        object_pairs_hook=lambda pairs: {int(k) if k.isnumeric() else k: v for k, v in pairs}
    )


class Championship(models.Model):
    CHAMPIONSHIP_CHOICES = [
        ("f1", "Formula 1"),
        ("f2", "Formula 2"),
        ("fe", "Formula E"),
    ]
    year = models.IntegerField()
    series = models.CharField(
        max_length=255,
        choices=CHAMPIONSHIP_CHOICES
    )
    is_fantasy = models.BooleanField(default=False)
    is_tahmin = models.BooleanField(default=False)
    fastest_lap_point = models.PositiveSmallIntegerField(default=0)
    sprint_fastest_lap_point = models.PositiveSmallIntegerField(default=0)
    overtake_coefficient = models.FloatField()
    qualifying_coefficient = models.FloatField()
    finish_coefficient = models.FloatField()
    beginning_token = models.PositiveSmallIntegerField()
    starting_budget = models.DecimalField(max_digits=3, decimal_places=1)
    max_drivers_in_team = models.PositiveSmallIntegerField(default=8)
    price_img = models.FileField(null=True, blank=True)
    slug = models.SlugField(unique=True, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year', 'series'], name='unique_year_series'),
        ]
        ordering = ["-year", "series"]

    def __str__(self):
        return f"{self.year} {self.get_series_display()} Şampiyonası"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.year}-{self.series}"
        super().save(*args, **kwargs)

    def coefficient(self, tactic):
        if tactic == RaceTeam.GEÇİŞ:
            return self.overtake_coefficient
        elif tactic == RaceTeam.SIRALAMA:
            return self.qualifying_coefficient
        elif tactic == RaceTeam.FİNİŞ:
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
                    fp1_datetime__gt=timezone.now(),
                    fantasy_ready=True
                ).latest("fp1_datetime")
            elif league == "tahmin":
                return self.races.filter(
                    datetime__gt=timezone.now(),
                    quali_datetime__lt=timezone.now()
                ).latest("quali_datetime")
        except Race.DoesNotExist:
            return None

    def get_absolute_url(self):
        return reverse("formula:race_list", kwargs={'series': self.series, 'year': self.year})


class Circuit(models.Model):
    slug = models.SlugField(primary_key=True)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255, null=True, blank=True)
    country = CountryField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    url = models.URLField(unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("formula:circuit_detail", kwargs={'pk': self.pk})


class Constructor(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    country = CountryField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    championship = models.ManyToManyField(Championship, through='ChampionshipConstructor', related_name='constructors')

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("formula:constructor_detail", kwargs={'slug': self.slug})


class Driver(models.Model):
    forename = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    number = models.IntegerField(blank=True, null=True)
    code = models.CharField(max_length=3, blank=True, null=True)
    country = CountryField(null=True, blank=True)
    dob = models.DateField(blank=True, null=True)
    url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ["forename", "surname"]

    def __str__(self):
        return self.name

    @property
    def name(self):
        return f"{self.forename} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("formula:driver_detail", kwargs={'slug': self.slug})


class Race(models.Model):
    name = models.CharField(max_length=255)
    championship = models.ForeignKey(Championship, on_delete=models.RESTRICT, related_name='races', null=True)
    round = models.IntegerField()
    country = CountryField()
    circuit = models.ForeignKey(Circuit, on_delete=models.RESTRICT, related_name='races', null=True)
    datetime = models.DateTimeField()
    fp1_datetime = models.DateTimeField(null=True, blank=True)
    fp2_datetime = models.DateTimeField(null=True, blank=True)
    fp3_datetime = models.DateTimeField(null=True, blank=True)
    quali_datetime = models.DateTimeField(null=True, blank=True)
    sprint_shootout_datetime = models.DateTimeField(null=True, blank=True)
    sprint_datetime = models.DateTimeField(null=True, blank=True)
    fantasy_ready = models.BooleanField(default=False)
    wikilink = models.URLField(blank=True)
    drivers = models.ManyToManyField(Driver, through='RaceDriver', related_name='attended_races')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['championship', 'round'], name='unique_championship_round'),
        ]
        ordering = ["-datetime"]

    def __str__(self):
        return f"{self.championship.year} {self.name}"

    def get_absolute_url(self):
        return reverse(
            "formula:race_detail",
            kwargs={'series': self.championship.series, 'year': self.championship.year, "round": self.round}
        )

    def get_tahmin_url(self):
        return reverse(
            "formula:tahmin:race_tahmins",
            kwargs={'series': self.championship.series, 'year': self.championship.year, "round": self.round}
        )

    @cached_property
    def next(self):
        try:
            return self.get_next_by_datetime(championship__series=self.championship.series)
        except Race.DoesNotExist:
            return None

    @cached_property
    def previous(self):
        try:
            return self.get_previous_by_datetime(championship__series=self.championship.series)
        except Race.DoesNotExist:
            return None

    @cached_property
    def top10(self):
        top10_drivers = self.driver_instances.select_related("driver").filter(
            result__isnull=False,
            result__lte=10
        ).only("race", "driver", "result").order_by("result")
        return top10_drivers


class RaceDriver(models.Model):
    DISCOUNT_COEFFICIENTS = (
        Decimal("0.6"),
        Decimal("0.13"),
        Decimal("-0.0044"),
        Decimal("0.000054")
    )
    OVERTAKE_DOUBLE_POINT_THRESHOLD = 10
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='driver_instances')
    driver = models.ForeignKey(Driver, on_delete=models.RESTRICT, related_name='race_instances')
    championship_constructor = models.ForeignKey("ChampionshipConstructor", null=True, on_delete=models.SET_NULL, related_name='race_drivers')
    price = models.DecimalField(max_digits=3, decimal_places=1)
    discount = models.BooleanField(default=False)
    qualy = models.PositiveIntegerField(blank=True, null=True)
    grid_sprint = models.PositiveIntegerField(blank=True, null=True)
    sprint = models.PositiveIntegerField(blank=True, null=True)
    sprint_fastest_lap = models.BooleanField(default=False)
    grid = models.PositiveIntegerField(blank=True, null=True)
    result = models.PositiveIntegerField(blank=True, null=True)
    fastest_lap = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['race', 'driver'], name='unique_racedriver'),
        ]
        ordering = [
            "race",
            "championship_constructor",
            "driver__number"
        ]

    def __str__(self):
        return f"{self.race}-{self.driver}"

    def qualy_point(self, tactic=None):
        if not any((self.qualy, self.grid_sprint, self.sprint, self.grid, self.result)):
            return None
        coefficient = self.race.championship.coefficient(tactic) if tactic == RaceTeam.SIRALAMA else 1
        return round(POINTS["qualy"].get(self.qualy, 0) * coefficient, 1)

    def _sprint_point(self):
        return POINTS["sprint"][self.race.championship.get_series_display()].get(self.sprint, 0)

    def _feature_point(self):
        return POINTS["race"].get(self.result, 0)

    def race_point(self, tactic=None):
        if not any((self.qualy, self.grid_sprint, self.sprint, self.grid, self.result)):
            return None
        coefficient = self.race.championship.coefficient(tactic) if tactic == RaceTeam.FİNİŞ else 1
        fastest_lap_point = self.race.championship.fastest_lap_point
        sprint_fastest_lap_point = self.race.championship.sprint_fastest_lap_point
        return round(
            (
                self._feature_point() +
                self._sprint_point() +
                (self.fastest_lap * fastest_lap_point) +
                (self.sprint_fastest_lap * sprint_fastest_lap_point)
            ) * coefficient,
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
            bottom_to_top = max(0, self.OVERTAKE_DOUBLE_POINT_THRESHOLD - self.sprint)
            top_to_top = max(0, self.OVERTAKE_DOUBLE_POINT_THRESHOLD - self.grid_sprint)
            return raw + bottom_to_top - top_to_top

    def _feature_overtake_point(self):
        if not self.grid or not self.result:
            return 0
        elif self.grid < self.result:
            return 0
        else:
            raw = (self.grid - self.result)
            bottom_to_top = max(0, self.OVERTAKE_DOUBLE_POINT_THRESHOLD - self.result)
            top_to_top = max(0, self.OVERTAKE_DOUBLE_POINT_THRESHOLD - self.grid)
            return raw + bottom_to_top - top_to_top

    def overtake_point(self, tactic=None):
        if not any((self.qualy, self.grid_sprint, self.sprint, self.grid, self.result)):
            return None
        coefficient = self.race.championship.coefficient(tactic) if tactic == RaceTeam.GEÇİŞ else 1
        return round(
            (self._sprint_overtake_point() + self._feature_overtake_point()) * coefficient,
            1
        )

    def total_point(self, tactic=None):
        if not any((self.qualy, self.grid_sprint, self.sprint, self.grid, self.result)):
            if tactic:
                return 0.0
            return None
        return round((self.overtake_point(tactic)) + (self.qualy_point(tactic)) + (self.race_point(tactic)), 1)

    def discounted_price(self):
        if self.discount:
            discount = sum(
                self.DISCOUNT_COEFFICIENTS[power] * self.price ** power
                for power
                in range(4)
            )
            return round(self.price - discount, 1)
        return self.price

    def instances(self):
        return self.raceteamdrivers.count()

    @cache
    def tahmin_count(self, position):
        return getattr(self, f"prediction_{position}").count()

    def tahmin_score(self, position):
        if self.result == position:
            count = self.tahmin_count(position)
            if 0 < count < 20:
                return ceil((20 - count) ** 2 / 2)
        return 0


class RaceTeam(models.Model):
    GEÇİŞ = "G"
    SIRALAMA = "S"
    FİNİŞ = "F"
    TACTIC_CHOICES = [
        (GEÇİŞ, "Geçiş"),
        (SIRALAMA, "Sıralama"),
        (FİNİŞ, "Finiş"),
    ]
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='team_instances')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fantasy_instances')
    token = models.IntegerField()
    budget = models.DecimalField(max_digits=4, decimal_places=1)
    tactic = models.CharField(
        max_length=8,
        choices=TACTIC_CHOICES
    )
    race_drivers = models.ManyToManyField(RaceDriver, through="RaceTeamDriver", related_name='raceteams', blank=True)

    class Meta:
        ordering = [
            "race",
            "user"
        ]

    def __str__(self):
        return f"{self.race}-{self.user}"

    @cached_property
    def total_point(self):
        return round(sum(race_driver.total_point(self.tactic) for race_driver in self.race_drivers.all()), 1)

    def overtake_point(self):
        return round(sum(race_driver.total_point(self.GEÇİŞ) for race_driver in self.race_drivers.all()), 1)

    def qualy_point(self):
        return round(sum(race_driver.total_point(self.SIRALAMA) for race_driver in self.race_drivers.all()), 1)

    def race_point(self):
        return round(sum(race_driver.total_point(self.FİNİŞ) for race_driver in self.race_drivers.all()), 1)

    def none_point(self):
        return round(sum(race_driver.total_point() or 0 for race_driver in self.race_drivers.all()), 1)

    def total_worth(self):
        return round(sum(race_driver.price for race_driver in self.race_drivers.all()) + self.budget, 1)


class RaceTeamDriver(models.Model):
    raceteam = models.ForeignKey(RaceTeam, on_delete=models.CASCADE, related_name='raceteamdrivers')
    racedriver = models.ForeignKey(RaceDriver, on_delete=models.CASCADE, related_name='raceteamdrivers')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['raceteam', 'racedriver'], name='unique_raceteam_racedriver'),
        ]
        ordering = ["racedriver__race", "raceteam__user__first_name", "-racedriver__price"]

    def __str__(self):
        return f"{self.raceteam}-{self.racedriver}"

    def total_point(self):
        return self.racedriver.total_point(self.raceteam.tactic)


class ChampionshipConstructor(models.Model):
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE, related_name='constructor_instances')
    constructor = models.ForeignKey(Constructor, on_delete=models.CASCADE, related_name='championship_instances')
    garage_order = models.IntegerField()
    bgcolor = ColorField(default="#f8f9fa")
    fontcolor = ColorField(default="#000000")
    alternative_bgcolor = ColorField(default="#f8f9fa")
    alternative_fontcolor = ColorField(default="#000000")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['championship', 'constructor'], name='unique_championship_constructor'),
            models.UniqueConstraint(fields=['championship', 'garage_order'], name='unique_championship_garage_order'),
        ]
        ordering = ["championship", "garage_order"]

    def __str__(self):
        return f"{self.championship} - {self.constructor}"
