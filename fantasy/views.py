from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from .models import *


class ChampionshipDetailView(DetailView):
    model = Championship


class ChampionshipDriverListView(ListView):
    model = Driver
    template_name = "fantasy/season_driver_list.html"

    def get_queryset(self):
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('slug')
        )
        queryset = Driver.objects.filter(
            attended_races__in=Race.objects.filter(
                championship=championship
            )
        ).distinct()
        # queryset = queryset.order_by('forename')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('slug')
        )
        race_list = Race.objects.filter(
            championship=championship
        )

        driver_list = self.get_queryset()
        race_driver_dict = {}
        for driver in driver_list:
            race_driver_dict[driver] = [
                RaceDriver.objects.filter(race=race, driver=driver).first()
                for race
                in race_list
            ]

        driver_count_dict = {}
        for driver in driver_list:
            driver_count_dict[driver] = [
                RaceTeamDriver.objects.filter(
                    racedriver__driver=driver,
                    racedriver__race=race
                ).count()
                for race
                in race_list
            ]
        tactic_count_dict = {}
        for tactic in "G", "S", "F":
            tactic_count_dict[tactic] = [
                RaceTeam.objects.filter(
                    tactic=tactic,
                    race=race
                ).count()
                for race
                in race_list
            ]

        context["tactic_count_dict"] = tactic_count_dict
        context["race_driver_dict"] = race_driver_dict
        context["driver_count_dict"] = driver_count_dict
        context["championship"] = championship
        context["race_list"] = race_list
        context["tabs"] = {
            "total_point": "Total Points",
            "qualy": "Qualifying",
            "grid": "Grid",
            "result": "Results",
            "overtake_point": "Overtake Points",
            "qualy_point": "Qualifying Points",
            "race_point": "Race Points",
            "price_with_currency": "Prices",
            "instances": "Count",
        }
        return context


class ChampionshipListView(ListView):
    model = Championship
    ordering = ["-year", "series"]


class DriverDetailView(DetailView):
    model = Driver


class DriverListView(ListView):
    model = Driver
    ordering = "forename"


class RaceDetailView(DetailView):
    model = Race

    def get_object(self):
        return get_object_or_404(
            Race,
            championship__slug=self.kwargs.get('slug'),
            round=self.kwargs.get('round')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["race_driver_list"] = RaceDriver.objects.filter(race=context["race"])
        context["race_team_list"] = RaceTeam.objects.filter(race=context["race"]).order_by("team__name")
        return context


class RaceListView(ListView):
    model = Race

    def get_queryset(self):
        races = Race.objects.filter(championship__slug=self.kwargs.get('slug'))
        queryset = races.order_by('round')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["championship"] = get_object_or_404(Championship, slug=self.kwargs.get("slug"))
        return context
