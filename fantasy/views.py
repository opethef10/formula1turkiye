from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, UpdateView

from .forms import *
from .models import *


class ChampionshipDetailView(DetailView):
    model = Championship
    slug_url_kwarg = "champ"


class DriverListView(ListView):
    model = Driver

    def get_queryset(self):
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        queryset = Driver.objects.filter(
            attended_races__in=Race.objects.filter(
                championship=championship
            )
        ).distinct().order_by('race_instances__championship_constructor__garage_order')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        race_list = Race.objects.filter(
            championship=championship
        ).order_by('round')

        driver_list = self.get_queryset()
        race_driver_dict = {
            driver: [
                RaceDriver.objects.filter(race=race, driver=driver).first()
                for race
                in race_list
            ]
            for driver
            in driver_list
        }

        driver_count_dict = {
            driver: [
                RaceTeamDriver.objects.filter(
                    racedriver__driver=driver,
                    racedriver__race=race
                ).count()
                for race
                in race_list
            ]
            for driver
            in driver_list
        }
        tactic_count_dict = {
            tactic: [
                RaceTeam.objects.filter(
                    tactic=tactic,
                    race=race
                ).count()
                for race
                in race_list
            ]
            for tactic
            in {"G", "S", "F"}
        }

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
    slug_url_kwarg = "driver_slug"


class RaceDetailView(DetailView):
    model = Race

    def get_object(self):
        return get_object_or_404(
            Race,
            championship__slug=self.kwargs.get('champ'),
            round=self.kwargs.get('round')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["race_driver_list"] = RaceDriver.objects.filter(
            race=context["race"]
        ).order_by(
            "championship_constructor__garage_order"
        )
        context["race_team_list"] = RaceTeam.objects.filter(
            race=context["race"]
        ).order_by(
            "team__account__first_name",
            "team__account__last_name"
        )
        context["tabs"] = {
            "drivers": "Drivers",
            "teams": "Teams",
            "kadrolar": "Kadrolar"
        }
        return context


class RaceListView(ListView):
    model = Race

    def get_queryset(self):
        races = Race.objects.filter(championship__slug=self.kwargs.get('champ'))
        queryset = races.order_by('round')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["championship"] = get_object_or_404(Championship, slug=self.kwargs.get('champ'))
        return context


class TeamListView(ListView):
    model = Team

    def get_queryset(self):
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        queryset = Team.objects.filter(
            championship=championship
        ).distinct()
        # queryset = queryset.order_by('forename')
        return queryset

    def get_context_data(self, **kwargs):
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        race_list = Race.objects.filter(
            championship=championship
        ).order_by('round')
        team_list = self.get_queryset()
        race_team_dict = {
            team: [
                RaceTeam.objects.filter(race=race, team=team).first()
                for race
                in race_list
            ]
            for team
            in team_list
        }
        context = super().get_context_data(**kwargs)
        context["championship"] = championship
        context["race_list"] = race_list
        context["race_team_dict"] = race_team_dict
        context["tabs"] = {
            "total_point": "Total Points",
        }
        return context


class TeamDetailView(DetailView):
    model = Team

    def get_object(self):
        return get_object_or_404(
            Team,
            championship__slug=self.kwargs.get('champ'),
            account__username=self.kwargs.get('username')
        )

    def get_context_data(self, **kwargs):
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        race_list = Race.objects.filter(
            championship=championship
        ).order_by('round')
        team = self.get_object()
        race_team_dict = {
            race: RaceTeam.objects.filter(race=race, team=team).first()
            for race
            in race_list
        }
        context = super().get_context_data(**kwargs)
        context["championship"] = championship
        context["race_team_dict"] = race_team_dict
        return context


class NewTeamView(LoginRequiredMixin, UpdateView):
    model = RaceTeam
    form_class = NewTeamForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        self.race = Race.objects.get(championship=self.championship, round=1)  # TODO: Update this to show current race

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["championship"] = self.championship
        return context

    def form_valid(self, form):
        team, created = Team.objects.get_or_create(
            account=self.request.user,
            championship=self.championship
        )
        if created:
            form.instance.race = self.race
            form.instance.team = team
        return super().form_valid(form)

    def get_object(self):
        try:
            return RaceTeam.objects.get(
                team__account=self.request.user,
                team__championship=self.championship,
                race=self.race
            )
        except RaceTeam.DoesNotExist:
            return

    def get_success_url(self):
        return self.object.team.get_absolute_url()
