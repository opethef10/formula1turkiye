import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, DetailView, RedirectView, TemplateView, UpdateView

from .forms import NewTeamForm, EditTeamForm, RaceDriverEditForm, RaceDriverFormSet
from .models import Championship, Circuit, Race, RaceDriver, RaceTeam, Team

logger = logging.getLogger("f1t")
HOURS = settings.HOURS


# @method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
class DriverListView(ListView):
    template_name = "fantasy/driver_list.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )

    def get_queryset(self):
        return RaceDriver.objects.prefetch_related(
            "raceteamdrivers"
        ).select_related(
            "driver",
            "race",
            "race__championship",
            "championship_constructor"
        ).filter(
            race__championship=self.championship
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race_list = Race.objects.prefetch_related("team_instances").select_related("championship").filter(
            championship=self.championship
        ).order_by("round")
        race_count = race_list.count()
        race_driver_dict = {}
        for rd in self.get_queryset():
            if rd.driver not in race_driver_dict:
                race_driver_dict[rd.driver] = [None] * race_count
            race_driver_dict[rd.driver][rd.race.round - 1] = rd

        tactic_count_dict = {tactic: [None] * race_count for tactic in {"Finiş", "Geçiş", "Sıralama"}}

        for race in race_list:
            race_tactic_sum_dict = dict(
                race.team_instances.order_by("tactic").values_list("tactic").annotate(tactic_count=Count("tactic"))
            )
            for tactic in {"Finiş", "Geçiş", "Sıralama"}:
                tactic_count_dict[tactic][race.round - 1] = race_tactic_sum_dict.get(tactic[0])
        context["tactic_count_dict"] = tactic_count_dict
        context["race_driver_dict"] = race_driver_dict
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


# @method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class ChampionshipListView(ListView):
    queryset = Championship.objects.filter(is_fantasy=True)
    ordering = ["-year", "series"]


class CircuitListView(ListView):
    model = Circuit


class CircuitDetailView(DetailView):
    model = Circuit


class LastRaceRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        champ_slug = self.kwargs.get('champ')
        championship = get_object_or_404(Championship, slug=champ_slug)
        latest_race = championship.latest_race()

        if latest_race:
            return reverse('fantasy:race_detail', kwargs={'champ': champ_slug, 'round': latest_race.round})
        else:
            raise Http404("No previous races found.")


# @method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class RaceDetailView(DetailView):
    model = Race

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )

    def get_object(self):
        return get_object_or_404(
            Race,
            championship=self.championship,
            round=self.kwargs.get('round')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race = self.object
        context["race_driver_list"] = race.driver_instances.select_related(
            "championship_constructor", "driver", "race", "race__championship"
        )
        context["race_team_list"] = race.team_instances.prefetch_related(
            "raceteamdrivers", "race_drivers", "raceteamdrivers__racedriver", "raceteamdrivers__racedriver__driver",
            "team__user", "team__championship", "race_drivers__race__championship",
            "raceteamdrivers__racedriver__race__championship"
        ).select_related(
            "team",
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


# @method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class RaceListView(ListView):

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )

    def get_queryset(self):
        return self.championship.races.select_related("circuit").order_by("round")

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            team_count = RaceTeam.objects.filter(
                team__user=self.request.user,
                team__championship__slug=self.kwargs.get('champ')
            ).count()
        else:
            team_count = None
        context = super().get_context_data(**kwargs)
        context["race_team_count"] = team_count
        return context


# @method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
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
        race_list = Race.objects.select_related("championship").prefetch_related("team_instances").filter(
            championship=self.championship
        ).order_by("round")
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

        context = super().get_context_data(**kwargs)
        context["championship"] = self.championship
        context["race_list"] = race_list
        context["race_team_dict"] = race_team_dict
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
        ).order_by("round")
        team = self.get_object()

        race_team_dict = {race: None for race in race_list}
        for rt in RaceTeam.objects.prefetch_related(
            "raceteamdrivers", "raceteamdrivers__racedriver", "raceteamdrivers__racedriver__driver",
            "raceteamdrivers__racedriver__race", "raceteamdrivers__racedriver__race__championship",
            "race_drivers__race__championship"
        ).select_related("race", "team").filter(team=team):
            race_team_dict[rt.race] = rt
        context = super().get_context_data(**kwargs)
        context["championship"] = championship
        context["race_team_dict"] = race_team_dict
        return context


class TeamNewEditBaseView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = RaceTeam
    success_message = "Form başarıyla gönderildi!"
    error_message = "Form gönderilemedi, form hatalarını düzelttikten sonra tekrar deneyin!"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        self.next_race = self.championship.next_race("fantasy")
        self.race = self.next_race or self.championship.next_race("tahmin")

    def get(self, request, *args, **kwargs):
        if self.next_race is None:
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
        for key, value in form.cleaned_data.items():
            if isinstance(value, QuerySet):
                form.cleaned_data[key] = [str(racedriver.driver) for racedriver in value]
        logger.info(
            f"FANTASY {self.championship.series.upper()}: {self.request.user.get_full_name()}: {form.cleaned_data}"
        )
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, self.error_message)
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
