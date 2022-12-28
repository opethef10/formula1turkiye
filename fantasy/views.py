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
        )
        queryset = queryset.order_by('forename')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["championship"] = Championship.objects.get(
            slug=self.kwargs.get("slug")
        )
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
