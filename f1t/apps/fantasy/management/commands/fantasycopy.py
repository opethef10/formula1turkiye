from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

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

        with transaction.atomic():
            championship = Championship.objects.get(series=series, year=timezone.now().year)
            prev_race = championship.latest_race()
            next_race = prev_race.next

            if not next_race:
                self.stderr.write("No next race found")
                raise Race.DoesNotExist("No next race found")

            prev_race_drivers = prev_race.driver_instances.all()
            prev_raceteams = prev_race.team_instances.all()

            # SAFELY create RaceDriver instances without updating prices
            for prd in prev_race_drivers:
                # Only create if doesn't exist - never update existing
                nrd, created = RaceDriver.objects.get_or_create(
                    race=next_race,
                    driver=prd.driver,
                    defaults={
                        'championship_constructor': prd.championship_constructor,
                        'price': prd.price  # Only set on creation
                    }
                )
                if created:
                    self.stdout.write(f"Created RaceDriver {nrd}")
                else:
                    # Log but don't modify existing driver
                    self.stdout.write(f"RaceDriver {nrd} already exists (price remains {nrd.price})")

            for prt in prev_raceteams:
                # Calculate new values but only use them for new teams
                new_budget = prt.budget + 5 if increase_budget else prt.budget
                new_token = 16 if set_token else prt.token

                # Create team if doesn't exist
                nrt, created = RaceTeam.objects.get_or_create(
                    race=next_race,
                    user=prt.user,
                    defaults={
                        'token': new_token,
                        'budget': new_budget,
                        'tactic': prt.tactic
                    }
                )

                if created:
                    self.stdout.write(f"Created RaceTeam {nrt}")
                else:
                    # Log existing team without modifying values
                    self.stdout.write(f"RaceTeam {nrt} already exists (budget: {nrt.budget}, token: {nrt.token})")

                # Get drivers ordered by price
                # Useful for ordering these race drivers in the fantasy detail page
                prev_drivers = prt.race_drivers.all().order_by("-price")

                # Only create driver assignments if team was just created
                if created:
                    for prd in prev_drivers:
                        try:
                            # Use existing driver if available
                            nrd = RaceDriver.objects.get(
                                race=next_race,
                                driver=prd.driver
                            )
                        except RaceDriver.DoesNotExist:
                            # Fallback: create with current price if missing
                            nrd = RaceDriver.objects.create(
                                race=next_race,
                                driver=prd.driver,
                                championship_constructor=prd.championship_constructor,
                                price=prd.price
                            )
                            self.stdout.write(f"Created missing RaceDriver {nrd}")

                        nrtd, created = RaceTeamDriver.objects.get_or_create(
                            raceteam=nrt,
                            racedriver=nrd
                        )
                        if created:
                            self.stdout.write(f"Created RaceTeamDriver {nrtd}")
