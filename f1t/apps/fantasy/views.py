import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.db.models import Count
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, DetailView, RedirectView, TemplateView, UpdateView

from .forms import NewTeamForm, EditTeamForm, RaceDriverEditForm, RaceDriverFormSet
from .models import Championship, Circuit, Race, RaceDriver, RaceTeam, Driver, Constructor, Rating

logger = logging.getLogger("f1t")
HOURS = settings.HOURS


# @method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
class DriverStatsView(ListView):
    template_name = "fantasy/driver_stats.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
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


class SeasonsListView(ListView):
    allow_empty = False
    model = Championship
    template_name = "fantasy/seasons_list.html"

    def get_queryset(self):
        championships = Championship.objects.filter(series=self.kwargs.get("series")).order_by('year')

        # Create a dictionary to organize championships by decade
        championship_dict = {}
        for championship in championships:
            decade = championship.year // 10 * 10
            if decade not in championship_dict:
                championship_dict[decade] = []
            championship_dict[decade].append(championship)

        return championship_dict

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["series"] = f"Formula {self.kwargs.get('series')[-1]}"
        return context


class CircuitListView(ListView):
    model = Circuit


class CircuitDetailView(DetailView):
    model = Circuit


class AllDriverListView(ListView):
    model = Driver
    template_name = "fantasy/all_driver_list.html"


class ConstructorListView(ListView):
    model = Constructor


class ConstructorDetailView(DetailView):
    model = Constructor

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        constructor = self.object
        positions = range(1, settings.MAX_DRIVER_POSITION + 1)
        race_range = range(1, settings.MAX_RACES_IN_SEASON + 1)
        context["positions"] = positions
        context["race_range"] = race_range

        race_results = RaceDriver.objects.filter(
            race__datetime__lte=timezone.now(),
            championship_constructor__constructor=constructor
        )
        # constructor.race_instances.select_related("race__championship").filter(race__datetime__lte=timezone.now())
        # Fetching counts for grid and result instances in a single query
        annotated_grid_data = race_results.values('grid').annotate(grid_count=Count('*'))
        annotated_result_data = race_results.values('result').annotate(result_count=Count('*'))

        # Creating dictionaries to map counts for each position
        grid_counts = {data['grid']: data['grid_count'] for data in annotated_grid_data}
        result_counts = {data['result']: data['result_count'] for data in annotated_result_data}

        # championships = Championship.objects.filter(
        #     id__in=race_results.values_list("race__championship", flat=True)
        # )
        # race_results_dict = {
        #     championship:
        #         [None] * settings.MAX_RACES_IN_SEASON
        #         for championship
        #         in championships
        # }
        # for rr in race_results:
        #     race_results_dict[rr.race.championship][rr.race.round - 1] = rr

        # Creating grid_list and result_list using the counts
        context["grid_list"] = [grid_counts.get(pos) for pos in positions]
        context["result_list"] = [result_counts.get(pos) for pos in positions]
        context["pole"] = grid_counts.get(1, 0)
        context["win"] = result_counts.get(1, 0)
        context["podium"] = sum(result_counts.get(pos, 0) for pos in (1, 2, 3))
        context["total_races"] = race_results.values_list('race').distinct().count()
        context["not_classified"] = result_counts.get(None, 0)
        context["first_race"] = race_results.earliest("race__datetime").race
        context["last_race"] = race_results.latest("race__datetime").race
        context["race_results"] = race_results.order_by("race__datetime")
        # context["race_results_dict"] = race_results_dict

        return context


class DriverDetailView(DetailView):
    model = Driver

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        driver = self.object
        positions = range(1, settings.MAX_DRIVER_POSITION + 1)
        race_range = range(1, settings.MAX_RACES_IN_SEASON + 1)
        context["positions"] = positions
        context["race_range"] = race_range

        race_results = driver.race_instances.select_related("race__championship").filter(race__datetime__lte=timezone.now())
        # Fetching counts for grid and result instances in a single query
        annotated_grid_data = race_results.values('grid').annotate(grid_count=Count('*'))
        annotated_result_data = race_results.values('result').annotate(result_count=Count('*'))
        annotated_flap_data = race_results.values('fastest_lap').annotate(flap_count=Count('*'))

        # Creating dictionaries to map counts for each position
        grid_counts = {data['grid']: data['grid_count'] for data in annotated_grid_data}
        result_counts = {data['result']: data['result_count'] for data in annotated_result_data}
        flap_counts = {data['fastest_lap']: data['flap_count'] for data in annotated_flap_data}

        championships = Championship.objects.filter(
            id__in=race_results.values_list("race__championship", flat=True)
        )
        race_results_dict = {
            championship:
                [None] * settings.MAX_RACES_IN_SEASON
                for championship
                in championships
        }
        for rr in race_results:
            race_results_dict[rr.race.championship][rr.race.round - 1] = rr

        # Creating grid_list and result_list using the counts
        context["grid_list"] = [grid_counts.get(pos) for pos in positions]
        context["result_list"] = [result_counts.get(pos) for pos in positions]
        context["pole"] = grid_counts.get(1, 0)
        context["win"] = result_counts.get(1, 0)
        context["flap"] = flap_counts.get(True, 0)
        context["hattrick"] = race_results.filter(result=1,grid=1,fastest_lap=True).count()
        context["podium"] = sum(result_counts.get(pos, 0) for pos in (1, 2, 3))
        context["total_races"] = race_results.count()
        context["not_classified"] = result_counts.get(None, 0)
        context["first_race"] = race_results.earliest("race__datetime").race
        context["last_race"] = race_results.latest("race__datetime").race
        context["race_results"] = race_results.order_by("race__datetime")
        context["race_results_dict"] = race_results_dict

        return context

class DriverResultsView(DetailView):
    model = Driver
    template_name = "fantasy/driver_results.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        driver = self.object
        context['race_results'] = driver.race_instances.select_related(
            "race__championship", "race__circuit", "championship_constructor", "championship_constructor__constructor",
        ).filter(
            race__datetime__lte=timezone.now()
        ).order_by(
            'race__datetime'
        )
        return context


class DriverWinsView(DriverResultsView):
    template_name = "fantasy/driver_wins.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['race_results'] = context['race_results'].filter(result=1)
        return context


class DriverPolesView(DriverResultsView):
    template_name = "fantasy/driver_poles.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['race_results'] = context['race_results'].filter(grid=1)
        return context


class DriverHatTricksView(DriverResultsView):
    template_name = "fantasy/driver_hattricks.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['race_results'] = context['race_results'].filter(result=1,grid=1,fastest_lap=True)
        return context


class DriverFastestLapsView(DriverResultsView):
    template_name = "fantasy/driver_flaps.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['race_results'] = context['race_results'].filter(fastest_lap=True)
        return context


class DriverPodiumsView(DriverResultsView):
    template_name = "fantasy/driver_podiums.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['race_results'] = context['race_results'].filter(result__in=[1, 2, 3])
        return context


class LastRaceRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )
        latest_race = championship.latest_race()

        if latest_race:
            return latest_race.get_absolute_url()
        else:
            raise Http404("No previous races found.")


# @method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class RaceDetailView(DetailView):
    model = Race

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_object(self):
        return get_object_or_404(
            Race.objects.select_related('championship'),
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
            "race_drivers__race__championship",
            "raceteamdrivers__racedriver__race__championship"
        ).select_related(
            "user",
            "race__championship"
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
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_queryset(self):
        return self.championship.races.select_related("circuit").order_by("round")

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            team_count = RaceTeam.objects.filter(
                user=self.request.user,
                race__championship=self.championship
            ).count()
        else:
            team_count = None
        context = super().get_context_data(**kwargs)
        context["race_team_count"] = team_count
        return context


# @method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
class FantasyStandingsView(ListView):
    template_name = "fantasy/fantasy_standings.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_queryset(self):
        return RaceTeam.objects.prefetch_related(
            "race_drivers", "race_drivers__race__championship"
        ).select_related(
            "race",
            "user"
        ).filter(
            race__championship=self.championship
        )

    def get_context_data(self, **kwargs):
        user_list = User.objects.filter(
            fantasy_instances__race__championship=self.championship
        ).distinct()

        race_list = Race.objects.select_related("championship").filter(
            championship=self.championship
        ).order_by("round")
        race_count = race_list.count()

        race_team_dict = {user: [None] * race_count for user in user_list}
        for rt in self.get_queryset():
            race_team_dict[rt.user][rt.race.round - 1] = rt

        context = super().get_context_data(**kwargs)
        context["race_list"] = race_list
        context["race_team_dict"] = race_team_dict
        context["tabs"] = {
            "total_point": "Toplam Puan",
        }
        return context


class FantasyUserProfileView(ListView):
    template_name = "fantasy/fantasy_user_profile.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )
        self.user = get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )

    def get_queryset(self):
        return RaceTeam.objects.prefetch_related(
            "race_drivers", "race_drivers__race__championship",
            "raceteamdrivers", "raceteamdrivers__racedriver", "raceteamdrivers__racedriver__driver",
            "raceteamdrivers__racedriver__race", "raceteamdrivers__racedriver__race__championship",
        ).select_related(
            "race",
            "user"
        ).filter(
            race__championship=self.championship,
            user=self.user
        )

    def get_context_data(self, **kwargs):
        race_list = Race.objects.select_related("championship").filter(
            championship=self.championship
        ).order_by("round")

        race_team_dict = {race: None for race in race_list}
        for rt in self.get_queryset():
            race_team_dict[rt.race] = rt
        context = super().get_context_data(**kwargs)
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
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
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
                user=self.request.user,
                race=self.race
            )
        except RaceTeam.DoesNotExist:
            return

    def get_success_url(self):
        return reverse(
            "formula:team_detail",
            kwargs={
                'series': self.championship.series,
                'year': self.championship.year,
                "username": self.object.user.username
            }
        )

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
            user=self.request.user,
            race__championship=self.championship
        )
        if teams.count() > 1:
            return redirect(
                reverse(
                    "formula:edit_team_form",
                    kwargs={'series': self.championship.series, 'year': self.championship.year}
                )
            )
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if not self.get_object():
            form.instance.race = self.race
            form.instance.user = self.request.user
        return super().form_valid(form)


class EditTeamView(TeamNewEditBaseView):
    form_class = EditTeamForm
    template_name = "fantasy/edit_team_form.html"

    def get(self, request, *args, **kwargs):
        teams = RaceTeam.objects.filter(
            user=self.request.user,
            race__championship=self.championship
        )
        if teams.count() <= 1:
            return redirect(
                reverse(
                    "formula:new_team_form",
                    kwargs={'series': self.championship.series, 'year': self.championship.year}
                )
            )
        else:
            return super().get(request, *args, **kwargs)


class RaceDriverUpdateView(UserPassesTestMixin, UpdateView):
    model = RaceDriver
    form_class = RaceDriverEditForm
    template_name = "fantasy/race_edit.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = RaceDriverFormSet(
            queryset=RaceDriver.objects.filter(
                race__championship=self.championship,
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
            championship=self.championship,
            round=self.kwargs.get('round')
        )

    def test_func(self):
        return self.request.user.is_staff


class SeasonRatingView(ListView):
    allow_empty = False
    template_name = "fantasy/season_ratings.html"
    model = Rating

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_queryset(self):
        return Rating.objects.select_related('race', 'race__championship').filter(
            race__championship=self.championship
        )

class SeriesRatingView(ListView):
    allow_empty = False
    template_name = "fantasy/series_ratings.html"
    model = Rating

    def get_queryset(self):
        return Rating.objects.select_related('race', 'race__championship').filter(
            race__championship__series=self.kwargs.get("series")
        )

    def get_context_data(self):
        context = super().get_context_data()
        context["series"] = self.kwargs.get('series')
        context["series_display"] = f"Formula {self.kwargs.get('series')[-1]}"
        return context
