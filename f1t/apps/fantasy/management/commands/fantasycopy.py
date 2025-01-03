from django.core.management.base import BaseCommand
from django.utils import timezone

from ...models import Championship, Race, RaceDriver, RaceTeam, RaceTeamDriver


class Command(BaseCommand):
    help = "Copies the Fantasy Lig elements from previous race to next race"

    def add_arguments(self, parser):
        parser.add_argument("series", choices=['f1', 'f2'])
        parser.add_argument("--budget", action='store_true', help="Increase budget by 5₺")
        parser.add_argument("--token", action='store_true', help="Adjust token to 16")

    def handle(self, *args, **options):
        series = options["series"]
        increase_budget = options["budget"]
        set_token = options["token"]
        championship = Championship.objects.get(series=series, year=timezone.now().year)
        prev_race = championship.latest_race()
        next_race = prev_race.next
        if not next_race:
            self.stderr.write("No next race found")
            raise Race.DoesNotExist("No next race found")
        prev_race_drivers = prev_race.driver_instances.all()
        prev_raceteams = prev_race.team_instances.all()

        for prd in prev_race_drivers:
            nrd, created = RaceDriver.objects.get_or_create(
                race=next_race,
                driver=prd.driver,
                championship_constructor=prd.championship_constructor,
                price=prd.price
            )
            if created:
                self.stdout.write(f"Created RaceDriver {nrd}")

        for prt in prev_raceteams:
            nrt, created = RaceTeam.objects.get_or_create(
                race=next_race,
                user=prt.user,
                token=16 if set_token else prt.token,
                budget=prt.budget + 5 if increase_budget else prt.budget,
                tactic=prt.tactic
            )
            if created:
                self.stdout.write(f"Created RaceTeam {nrt}")

            for prd in prt.race_drivers.all().order_by("-price"):
                nrd = RaceDriver.objects.get(race=next_race, driver=prd.driver)
                nrtd, created = RaceTeamDriver.objects.get_or_create(
                    raceteam=nrt,
                    racedriver=nrd
                )
                if created:
                    self.stdout.write(f"Created RaceTeamDriver {nrtd}")
