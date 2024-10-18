from datetime import timezone as dt_timezone
import json

import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from f1t.apps.fantasy.models import Race, Championship, Circuit

server_timezone = timezone.get_current_timezone()

# Convert times to server timezone
def convert_to_server_timezone(dt):
    if dt:
        # No need to call make_aware, since dt is already timezone-aware (it has UTC)
        return dt.astimezone(server_timezone)
    
# Function to handle the session names mapping for different series
def get_session_times(sessions, series):
    if series == 'f2':
        # Mapping specific to F2
        fp1_time = convert_to_server_timezone(parse_datetime(sessions.get('practice'))) if sessions.get('practice') else None
        gp_time = convert_to_server_timezone(parse_datetime(sessions.get('feature'))) if sessions.get('feature') else None
        quali_time = convert_to_server_timezone(parse_datetime(sessions.get('qualifying'))) if sessions.get('qualifying') else None
        sprint_time = convert_to_server_timezone(parse_datetime(sessions.get('sprint'))) if sessions.get('sprint') else None
        fp2_time = fp3_time = sprint_shootout_time = None  # F2 doesn't have these sessions
    else:
        # Default mapping for other series like F1
        fp1_time = convert_to_server_timezone(parse_datetime(sessions.get('fp1'))) if sessions.get('fp1') else None
        fp2_time = convert_to_server_timezone(parse_datetime(sessions.get('fp2'))) if sessions.get('fp2') else None
        fp3_time = convert_to_server_timezone(parse_datetime(sessions.get('fp3'))) if sessions.get('fp3') else None
        quali_time = convert_to_server_timezone(parse_datetime(sessions.get('qualifying'))) if sessions.get('qualifying') else None
        sprint_time = convert_to_server_timezone(parse_datetime(sessions.get('sprint'))) if sessions.get('sprint') else None
        sprint_shootout_time = convert_to_server_timezone(parse_datetime(sessions.get('sprintQualifying'))) if sessions.get('sprintQualifying') else None
        gp_time = convert_to_server_timezone(parse_datetime(sessions.get('gp'))) if sessions.get('gp') else None

    return fp1_time, fp2_time, fp3_time, quali_time, sprint_shootout_time, sprint_time, gp_time

class Command(BaseCommand):
    help = 'Cross-check race data from a remote JSON with the database'

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, default=timezone.now().year, help='Year of the championship')
        parser.add_argument('--series', type=str, default='f1', choices=['f1', 'f2', 'fe'], help='Series of the championship (f1, f2, fe)')

    def handle(self, *args, **options):
        year = options['year']
        series = options['series']

        # Construct the URL based on the series and year
        url = f'https://raw.githubusercontent.com/sportstimes/f1/main/_db/{series}/{year}.json'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            self.stderr.write(f"Failed to fetch the data: {e}")
            return

        # Fetch the championship from the database based on the series and year
        try:
            championship = Championship.objects.get(year=year, series=series)
        except Championship.DoesNotExist:
            self.stderr.write(f"Championship for {series.upper()} {year} does not exist.")
            return

        races = data.get('races', [])
        if races:
            self.stdout.write("F1T database vs F1Calendar.com JSON data:")

        # Manually enumerate the rounds starting from 1
        for race_round, race_data in enumerate(races, start=1):
            sessions = race_data.get('sessions', {})
            fp1_time, fp2_time, fp3_time, quali_time, sprint_shootout_time, sprint_time, gp_time = get_session_times(sessions, series)
            race_name = race_data['name']
            location = race_data['location']
            latitude = race_data['latitude']
            longitude = race_data['longitude']
            # sessions = race_data['sessions']
            
            # Attempt to find the race in the database
            try:
                race = Race.objects.get(championship=championship, round=race_round)
            except Race.DoesNotExist:
                self.stderr.write(f"Race not found in DB: {race_name} (Round {race_round})")
                continue

            # Compare session datetimes
            mismatches = []

            # Convert race times to server timezone for comparison
            race_fp1 = race.fp1_datetime.astimezone(server_timezone) if race.fp1_datetime else None
            race_fp2 = race.fp2_datetime.astimezone(server_timezone) if race.fp2_datetime else None
            race_fp3 = race.fp3_datetime.astimezone(server_timezone) if race.fp3_datetime else None
            race_quali = race.quali_datetime.astimezone(server_timezone) if race.quali_datetime else None
            race_sprint = race.sprint_datetime.astimezone(server_timezone) if race.sprint_datetime else None
            race_sprint_shootout = race.sprint_shootout_datetime.astimezone(server_timezone) if race.sprint_shootout_datetime else None
            race_gp = race.datetime.astimezone(server_timezone) if race.datetime else None

            # Check each session time
            if race_fp1 != fp1_time:
                mismatches.append(f"FP1 time mismatch: {race_fp1} != {fp1_time}")
            if race_fp2 != fp2_time:
                mismatches.append(f"FP2 time mismatch: {race_fp2} != {fp2_time}")
            if race_fp3 != fp3_time:
                mismatches.append(f"FP3 time mismatch: {race_fp3} != {fp3_time}")
            if race_quali != quali_time:
                mismatches.append(f"Qualifying time mismatch: {race_quali} != {quali_time}")
            if race_sprint != sprint_time:
                mismatches.append(f"Sprint time mismatch: {race_sprint} != {sprint_time}")
            if race_sprint_shootout != sprint_shootout_time:
                mismatches.append(f"Sprint Shootout time mismatch: {race_sprint_shootout} != {sprint_shootout_time}")
            if race_gp != gp_time:
                mismatches.append(f"Race (GP) time mismatch: {race_gp} != {gp_time}")

            if mismatches:
                self.stdout.write(f"Mismatches for {race_name} (Round {race_round}):")
                for mismatch in mismatches:
                    self.stdout.write(f" - {mismatch}")
            else:
                self.stdout.write(f"Race {race_name} (Round {race_round}) is correct")
