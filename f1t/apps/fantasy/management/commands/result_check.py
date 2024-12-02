import requests
from django.core.management.base import BaseCommand
from f1t.apps.fantasy.models import Championship, Race, RaceDriver

class Command(BaseCommand):
    help = "Fetch and update race data from Jolpi.ca"

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help="Year of the championship")
        parser.add_argument('round', type=int, help="Round number of the race")
        parser.add_argument('--update', action='store_true', help="Update database with race result data")
        parser.add_argument('--ergast', action='store_true', help="Use Ergast API instead of Jolpica")

    def handle(self, *args, **options):
        series = "f1"
        year = options['year']
        round_number = options['round']
        update_flag = options['update']
        ergast = options['ergast']

        if ergast:
            api_url = f"https://ergast.com/api/{series}/{year}/{round_number}/results.json"
        else:
            api_url = f"https://api.jolpi.ca/ergast/{series}/{year}/{round_number}/results/"

        nullablePositions = {"R", "W", "D"}

        try:
            # Fetch data from the API
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()

            # Extract relevant data
            race_results = data["MRData"]["RaceTable"]["Races"][0]["Results"]

            # Get championship and race
            championship = Championship.objects.get(year=year, series=series)
            race = Race.objects.get(championship=championship, round=round_number)

            for result in race_results:
                driver_id = result["Driver"]["driverId"]
                position = result.get("positionText", "")
                if position in nullablePositions:
                    position = None
                grid = result.get("grid")

                # Find the RaceDriver instance
                race_driver = RaceDriver.objects.filter(race=race, driver__slug=driver_id).first()
                if race_driver:
                    if update_flag:
                        # Update the race data
                        race_driver.result = position
                        race_driver.grid = grid
                        race_driver.save()
                        self.stdout.write(f"Updated race data for {driver_id}")
                    else:
                        # Compare and print discrepancies
                        discrepancies = []
                        if str(race_driver.result) != str(position):
                            discrepancies.append(f"result: {race_driver.result} != {position}")
                        if str(race_driver.grid) != grid:
                            discrepancies.append(f"grid: {race_driver.grid} != {grid}")

                        if discrepancies:
                            self.stdout.write(f"Discrepancies for {driver_id}: {', '.join(discrepancies)}")
                else:
                    self.stdout.write(f"RaceDriver not found for driverId: {driver_id}")
        except requests.RequestException as e:
            self.stderr.write(f"Error fetching data from API: {e}")
        except Championship.DoesNotExist:
            self.stderr.write("Championship does not exist.")
        except Race.DoesNotExist:
            self.stderr.write("Race does not exist.")
        except Exception as e:
            self.stderr.write(f"An unexpected error occurred: {e}")
