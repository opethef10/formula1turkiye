from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import gettext as _
from django_countries.fields import CountryField
from colorfield.fields import ColorField


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
    fastest_lap_point = models.PositiveSmallIntegerField(default=0)
    sprint_fastest_lap_point = models.PositiveSmallIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year', 'series'], name='unique_championship_year_series'),
        ]
        ordering = ["-year", "series"]

    def __str__(self):
        return f"{self.year} {self.get_series_display()} {_('Şampiyonası')}"

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
        return reverse("formulapp:race_list", kwargs={'series': self.series, 'year': self.year})


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
        return reverse("formulapp:circuit_detail", kwargs={'pk': self.pk})


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
        return reverse("formulapp:constructor_detail", kwargs={'slug': self.slug})


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
        return reverse("formulapp:driver_detail", kwargs={'slug': self.slug})


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
            models.UniqueConstraint(fields=['championship', 'round'], name='unique_formula_championship_round'),
        ]
        ordering = ["-datetime"]

    def __str__(self):
        return f"{self.championship.year} {self.name}"

    def get_absolute_url(self):
        return reverse(
            "formulapp:race_detail",
            kwargs={'series': self.championship.series, 'year': self.championship.year, "round": self.round}
        )

    def get_tahmin_url(self):
        return reverse(
            "formulapp:tahmin:race_tahmins",
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
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='driver_instances')
    driver = models.ForeignKey(Driver, on_delete=models.RESTRICT, related_name='race_instances')
    championship_constructor = models.ForeignKey("ChampionshipConstructor", null=True, on_delete=models.SET_NULL, related_name='race_drivers')
    qualy = models.PositiveIntegerField(blank=True, null=True)
    grid_sprint = models.PositiveIntegerField(blank=True, null=True)
    sprint = models.PositiveIntegerField(blank=True, null=True)
    sprint_fastest_lap = models.BooleanField(default=False)
    grid = models.PositiveIntegerField(blank=True, null=True)
    result = models.PositiveIntegerField(blank=True, null=True)
    fastest_lap = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['race', 'driver'], name='unique_formula_racedriver'),
        ]
        ordering = [
            "race",
            "championship_constructor",
            "driver__number"
        ]

    def __str__(self):
        return f"{self.race}-{self.driver}"


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
            models.UniqueConstraint(fields=['championship', 'constructor'], name='unique_formula_championship_constructor'),
            models.UniqueConstraint(fields=['championship', 'garage_order'], name='unique_formula_championship_garage_order'),
        ]
        ordering = ["championship", "garage_order"]

    def __str__(self):
        return f"{self.championship} - {self.constructor}"
