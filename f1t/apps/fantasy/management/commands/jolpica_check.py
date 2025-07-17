import json
import requests
from django.core.management.base import BaseCommand

from f1t.apps.fantasy.models import Championship, Race, RaceDriver

SERIES = "f1"
NULLABLE_POSITIONS = {"R", "W", "D"}
API_BASE_URL = "https://api.jolpi.ca/ergast"


class Command(BaseCommand):
    help = "Fetch and optionally update race-related data (result, sprint, qualifying) from Jolpica API."

    def add_arguments(self, parser):
        parser.add_argument("datatype", choices=["results", "qualifying", "sprint"], help="Type of data to fetch")
        parser.add_argument("year", type=int, help="Year of the championship")
        parser.add_argument("round", type=int, help="Round number of the race")
        parser.add_argument("--update", action="store_true", help="Update the database with fetched data")
        parser.add_argument("--silent", action="store_true", help="Suppress non-error output")

    def handle(self, *args, **options):
        report = {
            'status': 'success',
            'discrepancies': [],
            'updated': [],
            'errors': []
        }
        silent = options["silent"]

        try:
            datatype = options["datatype"]
            year = options["year"]
            round_number = options["round"]
            update = options["update"]

            race = Race.objects.select_related('championship').get(
                championship__year=year,
                championship__series=SERIES,
                round=round_number
            )

            self.race_drivers = {
                rd.driver.slug: rd
                for rd in RaceDriver.objects.select_related("driver").filter(race=race)
            }

            if not silent:
                self.stdout.write(f"Fetching {datatype} data for {SERIES} {year} Round {round_number}...")
            session_data = self.fetch_data(year, round_number, datatype)

            match datatype:
                case "results":
                    self.handle_race(session_data, report, update, silent)
                case "qualifying":
                    self.handle_qualifying(session_data, report, update, silent)
                case "sprint":
                    self.handle_sprint(session_data, report, update, silent)
                case _:
                    raise ValueError(f"Unknown datatype: {datatype}")

        except Exception as e:
            report['status'] = 'error'
            error_msg = str(e)
            report['errors'].append(error_msg)
            if not silent:
                self.stderr.write(error_msg)

        return json.dumps(report)

    def fetch_data(self, year: int, round_number: int, datatype: str) -> dict:
        api_url = f"{API_BASE_URL}/{SERIES}/{year}/{round_number}/{datatype}/"
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        try:
            return data["MRData"]["RaceTable"]["Races"][0]
        except (KeyError, IndexError):
            raise ValueError(f"No data found for {SERIES} {year} Round {round_number} {datatype}.")

    def handle_race(self, session_data: dict, report: dict, update: bool, silent: bool):
        results = session_data["Results"]

        for result in results:
            driver_slug = result["Driver"]["driverId"]
            position = result.get("positionText", "")
            if position in NULLABLE_POSITIONS:
                position = None
            grid = result.get("grid")
            is_fastest = result.get("FastestLap", {}).get("rank") == "1"

            fields = {
                "result": position,
                "grid": grid,
                "fastest_lap": is_fastest,
            }

            self._update_or_compare(
                driver_slug,
                fields,
                report,
                update,
                silent,
            )

    def handle_sprint(self, session_data: dict, report: dict, update: bool, silent: bool):
        results = session_data["SprintResults"]

        for result in results:
            driver_slug = result["Driver"]["driverId"]
            position = result.get("positionText", "")
            if position in NULLABLE_POSITIONS:
                position = None

            fields = {
                "sprint": position,
                "grid_sprint": result.get("grid"),
            }
            self._update_or_compare(
                driver_slug,
                fields,
                report,
                update,
                silent,
            )

    def handle_qualifying(self, session_data: dict, report: dict, update: bool, silent: bool):
        results = session_data["QualifyingResults"]

        for result in results:
            driver_slug = result["Driver"]["driverId"]
            fields = {
                "q1": result.get("Q1", ""),
                "q2": result.get("Q2", ""),
                "q3": result.get("Q3", ""),
                "qualy": result.get("position", "")
            }

            self._update_or_compare(
                driver_slug,
                fields,
                report,
                update,
                silent
            )

    def _update_or_compare(self, driver_slug: str, result_fields: dict, report: dict, update: bool, silent: bool):
        race_driver = self.race_drivers.get(driver_slug)
        if not race_driver:
            error_msg = f"RaceDriver not found for driverId: {driver_slug}"
            report['errors'].append(error_msg)
            if not silent:
                self.stderr.write(error_msg)
            return

        driver_discrepancies = []
        for field, new_value in result_fields.items():
            old_value = getattr(race_driver, field)
            if str(old_value) != str(new_value):
                discrepancy = {
                    'driver': driver_slug,
                    'field': field,
                    'old_value': str(old_value),
                    'new_value': str(new_value)
                }
                driver_discrepancies.append(discrepancy)
                setattr(race_driver, field, new_value)

        if not driver_discrepancies:
            return


        if update:
            race_driver.save()
            report['updated'].extend(driver_discrepancies)
            if not silent:
                updated_fields = ', '.join(d['field'] for d in driver_discrepancies)
                self.stdout.write(f"Updated {updated_fields} for {driver_slug}")
        else:
            report['discrepancies'].extend(driver_discrepancies)
            if not silent:
                disc_strs = [f"{d['field']}: {d['old_value']} != {d['new_value']}" for d in driver_discrepancies]
                self.stdout.write(f"Discrepancies for {driver_slug}: {', '.join(disc_strs)}")
