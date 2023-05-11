import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, DetailView, TemplateView, UpdateView

from .forms import *
from .models import *

logger = logging.getLogger("f1tform")
HOURS = settings.HOURS


# @method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
class DriverListView(ListView):
    model = Driver

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )

    def get_queryset(self):
        return Driver.objects.prefetch_related(
            "race_instances", "race_instances__championship_constructor"
        ).filter(
            attended_races__in=Race.objects.filter(
                championship=self.championship
            )
        ).distinct().order_by(
            'race_instances__championship_constructor__garage_order',
            "number"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race_list = Race.objects.select_related("circuit", "championship").prefetch_related("team_instances").filter(
            championship=self.championship
        ).order_by('round')
        race_count = race_list.count()
        driver_list = self.get_queryset()
        race_driver_list = RaceDriver.objects.prefetch_related(
            "race__championship",
            "raceteamdrivers"
        ).select_related(
            "driver",
            "race"
        ).filter(
            race__championship=self.championship
        )
        race_driver_dict = {driver: [None] * race_count for driver in driver_list}
        for rd in race_driver_list:
            race_driver_dict[rd.driver][rd.race.round - 1] = rd

        driver_count_dict = {driver: [None] * race_count for driver in driver_list}
        for rd in race_driver_list:
            driver_count_dict[rd.driver][rd.race.round - 1] = rd.raceteamdrivers.count()

        tactic_count_dict = {tactic: [None] * race_count for tactic in {"Finiş", "Geçiş", "Sıralama"}}

        for race in race_list:
            race_tactic_sum_dict = dict(
                race.team_instances.order_by("tactic").values_list("tactic").annotate(tactic_count=Count("tactic"))
            )
            for tactic in {"Finiş", "Geçiş", "Sıralama"}:
                tactic_count_dict[tactic][race.round - 1] = race_tactic_sum_dict.get(tactic[0])

        context["tactic_count_dict"] = tactic_count_dict
        context["race_driver_dict"] = race_driver_dict
        context["driver_count_dict"] = driver_count_dict
        context["championship"] = self.championship
        context["race_list"] = race_list
        context["tabs"] = {
            "total_point": "Toplam Puan",
            "qualy": "Sıralama",
            "grid_sprint": "Sprint Grid",
            "sprint": "Sprint",
            "grid": "Grid",
            "result": "Yarış",
            "overtake_point": "Geçiş Puanı",
            "qualy_point": "Sıralama Puanı",
            "race_point": "Yarış Puanı",
            "price": "Fiyatlar",
            "discount": "Tanzim Pilotları",
            "instances": "Pilot Alış Sayıları",
        }
        return context


@method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class ChampionshipListView(ListView):
    model = Championship
    ordering = ["-year", "series"]
    queryset = Championship.objects.filter(is_fantasy=True).only("series", "year")


@method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class DriverDetailView(DetailView):
    model = Driver
    slug_url_kwarg = "driver_slug"


# @method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class RaceDetailView(DetailView):
    model = Race

    def get_object(self):
        return get_object_or_404(
            Race.objects.select_related("championship"),
            championship__slug=self.kwargs.get('champ'),
            round=self.kwargs.get('round')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["race_driver_list"] = RaceDriver.objects.prefetch_related(
            "race__championship"
        ).select_related(
            "championship_constructor", "driver", "race", "championship_constructor__constructor", "race__championship"
        ).filter(
            race=context["race"]
        ).order_by(
            "championship_constructor__garage_order",
            "driver__number"
        )
        context["race_team_list"] = RaceTeam.objects.prefetch_related(
            "raceteamdrivers", "race_drivers", "raceteamdrivers__racedriver", "raceteamdrivers__racedriver__driver",
            "team__user", "team__championship", "race_drivers__race__championship",
            "raceteamdrivers__racedriver__race__championship"
        ).select_related(
            "team",
        ).filter(
            race=context["race"]
        ).order_by(
            "team__user__first_name",
            "team__user__last_name"
        )
        context["tabs"] = {
            "drivers": "Sürücüler",
            "teams": "Takımlar",
            "kadrolar": "Kadrolar"
        }
        return context


@method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class RaceListView(ListView):
    model = Race

    def get_queryset(self):
        races = Race.objects.select_related("championship", "circuit").filter(
            championship__slug=self.kwargs.get('champ'))
        queryset = races.order_by('round')
        return queryset

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            team_count = RaceTeam.objects.filter(
                team__user=self.request.user,
                team__championship__slug=self.kwargs.get('champ')
            ).count()
        else:
            team_count = None
        context = super().get_context_data(**kwargs)
        context["championship"] = get_object_or_404(Championship, slug=self.kwargs.get('champ'))
        context["race_team_count"] = team_count
        return context


@method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
class TeamListView(ListView):
    model = Team

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )

    def get_queryset(self):
        queryset = Team.objects.select_related("user", "championship").prefetch_related("races_involved").filter(
            championship=self.championship
        ).distinct()
        # queryset = queryset.order_by('forename')
        return queryset

    def get_context_data(self, **kwargs):
        race_list = Race.objects.select_related("circuit", "championship").prefetch_related("team_instances").filter(
            championship=self.championship
        ).order_by('round')
        race_count = race_list.count()
        team_list = self.get_queryset()
        race_team_list = RaceTeam.objects.prefetch_related(
            "race_drivers", "race_drivers__race__championship"
        ).select_related(
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


class TeamDetailView(DetailView):
    model = Team

    def get_object(self):
        return get_object_or_404(
            Team,
            championship__slug=self.kwargs.get('champ'),
            user__username=self.kwargs.get('username')
        )

    def get_context_data(self, **kwargs):
        championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        race_list = Race.objects.select_related("championship").filter(
            championship=championship
        ).order_by('round')
        team = self.get_object()

        race_team_dict = {race: None for race in race_list}
        for rt in RaceTeam.objects.prefetch_related(
            "raceteamdrivers", "raceteamdrivers__racedriver", "raceteamdrivers__racedriver__driver"
        ).select_related("race", "team").filter(team=team):
            race_team_dict[rt.race] = rt
        context = super().get_context_data(**kwargs)
        context["championship"] = championship
        context["race_team_dict"] = race_team_dict
        return context


class TeamNewEditBaseView(LoginRequiredMixin, UpdateView):
    model = RaceTeam

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        self.race = self.championship.next_race("fantasy")

    def get(self, request, *args, **kwargs):
        if self.race is None:
            return TemplateView.as_view(template_name='expired.html')(request, *args, **kwargs)
        else:
            return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["championship"] = self.championship
        context["STARTING_BUDGET"] = self.championship.starting_budget
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            'request': self.request,
            'current_race': self.race
        })
        return kwargs

    def get_object(self):
        try:
            return RaceTeam.objects.get(
                team__user=self.request.user,
                team__championship=self.championship,
                race=self.race
            )
        except RaceTeam.DoesNotExist:
            return

    def get_success_url(self):
        return self.object.team.get_absolute_url()

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Form başarıyla gönderildi!")
        for key, value in form.cleaned_data.items():
            if isinstance(value, QuerySet):
                form.cleaned_data[key] = [str(racedriver.driver) for racedriver in value]
        logger.info(
            f"FANTASY {self.championship.series.upper()}: {self.request.user.get_full_name()}: {form.cleaned_data}"
        )
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Form gönderilemedi, form hatalarını düzelttikten sonra tekrar deneyin!")
        for key, value in form.cleaned_data.items():
            if isinstance(value, QuerySet):
                form.cleaned_data[key] = [str(racedriver.driver) for racedriver in value]
        logger.warning(
            f"FANTASY {self.championship.series.upper()}: {self.request.user.get_full_name()}: {form.cleaned_data} ERRORS: {form.errors!r}"
        )
        return response


class NewTeamView(TeamNewEditBaseView):
    form_class = NewTeamForm

    def get(self, request, *args, **kwargs):
        teams = RaceTeam.objects.filter(
            team__user=self.request.user,
            team__championship=self.championship
        )
        if teams.count() > 1:
            return redirect(reverse("fantasy:edit_team_form", kwargs={"champ": self.championship.slug}))
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        team, created = Team.objects.get_or_create(
            user=self.request.user,
            championship=self.championship
        )
        if created:
            form.instance.race = self.race
            form.instance.team = team
        return super().form_valid(form)


class EditTeamView(TeamNewEditBaseView):
    form_class = EditTeamForm
    template_name = "fantasy/edit_team_form.html"

    def get(self, request, *args, **kwargs):
        teams = RaceTeam.objects.filter(
            team__user=self.request.user,
            team__championship=self.championship
        )
        if teams.count() <= 1:
            return redirect(reverse("fantasy:new_team_form", kwargs={"champ": self.championship.slug}))
        else:
            return super().get(request, *args, **kwargs)


class RaceDriverUpdateView(UserPassesTestMixin, UpdateView):
    model = RaceDriver
    form_class = RaceDriverEditForm
    template_name = "fantasy/race_edit.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = RaceDriverFormSet(
            queryset=RaceDriver.objects.filter(
                race__championship__slug=self.kwargs.get('champ'),
                race__round=self.kwargs.get('round')
            )
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        formset = RaceDriverFormSet(request.POST)
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def form_valid(self, formset):
        self.object = self.get_object()
        instances = formset.save(commit=False)
        for instance in instances:
            instance.save()
        cache.clear()
        return HttpResponseRedirect(self.get_success_url())

    def get_object(self, queryset=None):
        return get_object_or_404(
            Race.objects.select_related("championship"),
            championship__slug=self.kwargs.get('champ'),
            round=self.kwargs.get('round')
        )

    def test_func(self):
        return self.request.user.is_staff
