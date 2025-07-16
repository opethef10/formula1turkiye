from collections import defaultdict
import json

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
        parser.add_argument('--silent', action='store_true', help='Suppress console output')

    def handle(self, *args, **options):
        result = {
            'status': 'success',
            'actions': defaultdict(int),
            'errors': []
        }

        try:
            with transaction.atomic():
                series = options["series"]
                increase_budget = options["budget"]
                set_token = options["token"]
                silent = options["silent"]

                championship = Championship.objects.get(series=series, year=timezone.now().year)
                prev_race = championship.latest_race()
                next_race = prev_race.next

                if not next_race:
                    error_msg = "No next race found"
                    result['errors'].append(error_msg)
                    result['status'] = 'error'
                    if not silent:
                        self.stderr.write(error_msg)
                    return json.dumps(result)

                # Process RaceDrivers
                for prd in prev_race.driver_instances.all():
                    nrd, created = RaceDriver.objects.get_or_create(
                        race=next_race,
                        driver=prd.driver,
                        defaults={
                            'championship_constructor': prd.championship_constructor,
                            'price': prd.price
                        }
                    )

                    action = 'created' if created else 'exists'
                    result['actions'][f'race_drivers_{action}'] += 1

                    if not silent:
                        self.stdout.write(f"RaceDriver {nrd} {action}")

                # Process RaceTeams
                for prt in prev_race.team_instances.all():
                    new_budget = prt.budget + 5 if increase_budget else prt.budget
                    new_token = 16 if set_token else prt.token

                    nrt, created = RaceTeam.objects.get_or_create(
                        race=next_race,
                        user=prt.user,
                        defaults={
                            'token': new_token,
                            'budget': new_budget,
                            'tactic': prt.tactic
                        }
                    )

                    action = 'created' if created else 'exists'
                    result['actions'][f'race_teams_{action}'] += 1

                    if not silent:
                        self.stdout.write(f"RaceTeam {nrt} {action}")

                    # Process Team Drivers only for new teams
                    if created:
                        # Get drivers ordered by price
                        # Useful for ordering these race drivers in the fantasy detail page
                        for prd in prt.race_drivers.all().order_by("-price"):
                            try:
                                nrd = RaceDriver.objects.get(
                                    race=next_race,
                                    driver=prd.driver
                                )
                            except RaceDriver.DoesNotExist:
                                result['errors'].append(f"Driver {prd.driver} not found for race {next_race}")
                                continue

                            nrtd, created = RaceTeamDriver.objects.get_or_create(
                                raceteam=nrt,
                                racedriver=nrd
                            )

                            action = 'created' if created else 'exists'
                            result['actions'][f'team_drivers_{action}'] += 1

                            if not silent:
                                self.stdout.write(f"RaceTeamDriver {nrtd} {action}")

        except Exception as e:
            result['status'] = 'error'
            result['errors'].append(str(e))
            if not silent:
                self.stderr.write(f"Error: {str(e)}")
            return json.dumps(result)

        return json.dumps(result)
