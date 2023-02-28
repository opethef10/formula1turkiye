from math import ceil

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView, UpdateView

from .forms import *
from .models import *


def tahmin_score(count):
    if not 0 < count < 20:
        return 0
    return ceil((20 - count) ** 2 / 2)


class ChampionshipListView(ListView):
    model = Championship
    ordering = ["-year", "series"]
    queryset = Championship.objects.filter(is_tahmin=True)
    template_name = "tahmin/championship_list.html"


class ChampionshipDetailView(DetailView):
    model = Championship
    slug_url_kwarg = "champ"
    template_name = "tahmin/championship_detail.html"


class RaceListView(ListView):
    model = Race
    allow_empty = False
    template_name = "tahmin/race_list.html"

    def get_queryset(self):
        races = Race.objects.filter(championship__slug=self.kwargs.get('champ'))
        queryset = races.order_by('round')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["championship"] = get_object_or_404(Championship, slug=self.kwargs.get('champ'))
        return context


class RaceDetailView(DetailView):
    model = Race
    template_name = "tahmin/race_detail.html"

    def get_object(self):
        return get_object_or_404(
            Race,
            championship__slug=self.kwargs.get('champ'),
            round=self.kwargs.get('round')
        )

    def get_context_data(self, **kwargs):
        current_race = self.get_object()
        race_tahmins = RaceTahmin.objects.filter(
            race=current_race
        ).order_by(
            "team__user__first_name",
            "team__user__last_name"
        )
        top10 = RaceDriver.objects.filter(
            race=current_race,
            result__isnull=False
        ).order_by("result")[:10]
        top10 = list(top10) + [None] * (10 - len(top10))

        counts = [
            race_tahmins.filter(**{f"prediction_{idx}": race_driver}).count()
            for idx, race_driver
            in enumerate(top10, 1)
        ]
        points = [tahmin_score(count) for count in counts]

        context = super().get_context_data(**kwargs)
        context["race_driver_list"] = RaceDriver.objects.filter(
            race=current_race
        ).order_by(
            "championship_constructor__garage_order",
            "driver__number"
        )
        context["race_team_list"] = race_tahmins
        context["top10"] = top10
        context["counts"] = counts
        context["points"] = points

        return context


class TeamListView(ListView):
    model = TahminTeam
    template_name = "tahmin/team_list.html"

    def get_queryset(self):
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        queryset = TahminTeam.objects.filter(
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
                RaceTahmin.objects.filter(race=race, team=team).first()
                for race
                in race_list
            ]
            for team
            in team_list
        }
        if self.request.user.is_authenticated:
            team_count = RaceTahmin.objects.filter(
                team__user=self.request.user,
                team__championship__slug=self.kwargs.get('champ')
            ).count()
        else:
            team_count = None

        context = super().get_context_data(**kwargs)
        context["championship"] = championship
        context["race_list"] = race_list
        context["race_team_dict"] = race_team_dict
        context["race_team_count"] = team_count
        context["tabs"] = {
            "total_point": "Total Points",
        }
        return context


class NewTahminView(LoginRequiredMixin, UpdateView):
    model = RaceTahmin
    form_class = NewTahminForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        try:
            self.race = Race.objects.filter(
                championship=self.championship,
                datetime__gt=timezone.now(),
                deadline__lt=timezone.now()
            ).latest("deadline")
        except Race.DoesNotExist:
            self.race = None

    def get(self, request, *args, **kwargs):
        if self.race is None:
            return TemplateView.as_view(template_name='expired.html')(request, *args, **kwargs)
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["championship"] = self.championship
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'current_race': self.race
        })
        return kwargs

    def get_object(self):
        try:
            return RaceTahmin.objects.get(
                team__user=self.request.user,
                team__championship=self.championship,
                race=self.race
            )
        except RaceTahmin.DoesNotExist:
            return

    def get_success_url(self):
        return self.race.get_tahmin_url()

    def form_valid(self, form):
        team, created = TahminTeam.objects.get_or_create(
            user=self.request.user,
            championship=self.championship
        )
        form.instance.race = self.race
        form.instance.team = team
        return super().form_valid(form)
