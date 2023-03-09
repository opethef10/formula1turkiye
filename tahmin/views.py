from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView, UpdateView

from .forms import *
from .models import *


class ChampionshipListView(ListView):
    model = Championship
    ordering = ["-year", "series"]
    queryset = Championship.objects.filter(is_tahmin=True)
    template_name = "tahmin/championship_list.html"


class RaceListView(ListView):
    model = Race
    template_name = "tahmin/race_list.html"

    def get_queryset(self):
        races = Race.objects.select_related("championship", "circuit").filter(championship__slug=self.kwargs.get('champ'))
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
        race_tahmins = RaceTahmin.objects.select_related(
            "team", *(f"prediction_{idx}" for idx in range(1, 11)), *(f"prediction_{idx}__driver" for idx in range(1, 11))
        ).filter(
            race=current_race
        ).order_by(
            "team__user__first_name",
            "team__user__last_name"
        )
        context = super().get_context_data(**kwargs)
        context["race_driver_list"] = RaceDriver.objects.select_related("driver").filter(
            race=current_race
        ).order_by(
            "championship_constructor__garage_order",
            "driver__number"
        )
        context["race_team_list"] = race_tahmins
        context["top10"] = current_race.top10
        context["counts"] = current_race.tahmin_counts
        context["points"] = current_race.tahmin_points
        context["before_race"] = current_race.datetime > timezone.now()

        return context


class TeamListView(ListView):
    model = TahminTeam
    template_name = "tahmin/team_list.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )

    def get_queryset(self):
        queryset = TahminTeam.objects.select_related("user", "championship").filter(
            championship=self.championship
        ).distinct()
        # queryset = queryset.order_by('forename')
        return queryset

    def get_context_data(self, **kwargs):
        race_list = Race.objects.select_related("circuit", "championship").prefetch_related("tahmin_team_instances").filter(
            championship=self.championship
        ).order_by('round')
        race_count = race_list.count()
        team_list = self.get_queryset()
        race_team_list = RaceTahmin.objects.select_related(
            "team",
            "race"
        ).filter(
            race__championship=self.championship
        )
        race_team_dict = {team: [None] * race_count for team in team_list}
        for rt in race_team_list:
            race_team_dict[rt.team][rt.race.round - 1] = rt

        if self.request.user.is_authenticated:
            team_count = race_team_list.filter(team__user=self.request.user).count()
        else:
            team_count = None

        context = super().get_context_data(**kwargs)
        context["championship"] = self.championship
        context["race_list"] = race_list
        context["race_team_dict"] = race_team_dict
        context["race_team_count"] = team_count
        context["tabs"] = {
            "total_point": "Toplam Puan",
        }
        return context


class NewTahminView(LoginRequiredMixin, UpdateView):
    model = RaceTahmin
    form_class = NewTahminForm
    success_url = reverse_lazy('sent')

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

    def form_valid(self, form):
        team, created = TahminTeam.objects.get_or_create(
            user=self.request.user,
            championship=self.championship
        )
        form.instance.race = self.race
        form.instance.team = team
        return super().form_valid(form)
