import json
from pathlib import Path

from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

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
        choices=[
            ("Formula 1", "Formula 1"),
            ("Formula 2", "Formula 2"),
            ("Formula E", "Formula E"),
        ]
    )
    slug = models.SlugField(unique=True, editable=False)

    def __str__(self):
        return f"{self.year} {self.series} Championship"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.year}-f{self.series[-1]}"
        super().save(*args, **kwargs)


class Circuit(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    country = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Constructor(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, editable=False)
    nationality = models.CharField(max_length=255, blank=True, null=True)
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
    nationality = models.CharField(max_length=255, blank=True, null=True)
    constructor = models.ForeignKey(Constructor, null=True, on_delete=models.SET_NULL, related_name='drivers')

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
    circuit = models.ForeignKey(Circuit, null=True, on_delete=models.SET_NULL, related_name='grand_prix')
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    drivers = models.ManyToManyField(Driver, through='RaceDriver', related_name='attended_races')
    teams = models.ManyToManyField('Team', through='RaceTeam', related_name='races_involved')

    def __str__(self):
        return f"{self.championship.year} {self.name}"


class RaceDriver(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='driver_instances')
    driver = models.ForeignKey(Driver, on_delete=models.RESTRICT, related_name='race_instances')
    price = models.DecimalField(max_digits=3, decimal_places=1)
    discount = models.BooleanField(default=False)
    qualy = models.IntegerField(blank=True, null=True)
    grid = models.IntegerField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)
    sprint = models.IntegerField(blank=True, null=True)
    fastest_lap = models.IntegerField(blank=True, null=True)

    def qualy_point(self, tactic=None):
        coefficient = 3.0 if tactic == "S" else 1
        return round(POINTS["qualy"].get(self.qualy, 0) * coefficient, 1)

    def sprint_point(self, tactic=None):
        coefficient = 1.7 if tactic == "F" else 1
        return round(POINTS["f1_sprint"].get(self.sprint, 0) * coefficient, 1)

    def race_point(self, tactic=None):
        coefficient = 1.7 if tactic == "F" else 1
        return round(
            (POINTS["race"].get(self.result, 0) + self.sprint_point() + (self.fastest_lap or 0)) * coefficient,
            1
        )

    def overtake_point(self, tactic=None):
        coefficient = 2.3 if tactic == "G" else 1
        if (self.grid is None) or (self.result is None):
            return 0
        elif (0 < self.grid <= 20) and (0 < self.result <= 20) and (self.grid > self.result):
            raw = (self.grid - self.result)
            bottom_to_top = (10 - self.result) if self.result < 10 else 0
            top_to_top = (10 - self.grid) if self.grid < 10 else 0
            return round((raw + bottom_to_top - top_to_top) * coefficient, 1)
        else:
            return 0

    def total_point(self, tactic=None):
        return round(self.overtake_point(tactic) + self.qualy_point(tactic) + self.race_point(tactic), 1)

    def __str__(self):
        return f"{self.race}-{self.driver}"


class Team(models.Model):
    account = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="teams")
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE, related_name="teams", null=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.account}'s Team: {self.name}"


class RaceTeam(models.Model):
    race = models.ForeignKey(Race, on_delete=models.CASCADE, related_name='team_instances')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='race_instances')
    token = models.IntegerField()
    budget = models.DecimalField(max_digits=4, decimal_places=1)
    tactic = models.CharField(max_length=8)
    race_drivers = models.ManyToManyField(RaceDriver, through="RaceTeamDriver", related_name='raceteams', blank=True)

    def __str__(self):
        return f"{self.race}-{self.team}"

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
        return round(
            self.racedriver.overtake_point(self.raceteam.tactic) +
            self.racedriver.qualy_point(self.raceteam.tactic) +
            self.racedriver.race_point(self.raceteam.tactic),
            1
        )


class ChampionshipConstructor(models.Model):
    championship = models.ForeignKey(Championship, on_delete=models.CASCADE, related_name='constructor_instances')
    constructor = models.ForeignKey(Constructor, on_delete=models.CASCADE, related_name='championship_instances')
    garage_order = models.IntegerField()

    def __str__(self):
        return f"{self.championship} - {self.constructor}"
