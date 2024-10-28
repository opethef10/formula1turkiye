import logging
from statistics import mean, median

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.cache import cache
from django.db.models import Count, Max
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
from .models import Championship, Circuit, Race, RaceDriver, RaceTeam, Driver, Constructor

logger = logging.getLogger("f1t")
HOURS = settings.HOURS


# @method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
class FantasyStatsView(ListView):
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


class SeasonStatsView(ListView):
    template_name = "fantasy/season_stats.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_queryset(self):
        return RaceDriver.objects.select_related(
            "driver",
            "race",
            "race__championship",
            "championship_constructor"
        ).filter(
            race__championship=self.championship
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race_drivers = self.get_queryset()
        race_list = Race.objects.select_related("championship").filter(
            championship=self.championship
        ).order_by("round")
        race_count = race_list.count()
        race_driver_dict = {}
        for rd in race_drivers:
            if rd.driver not in race_driver_dict:
                race_driver_dict[rd.driver] = [None] * race_count
            race_driver_dict[rd.driver][rd.race.round - 1] = rd

        context['winners'] = Driver.objects.filter(
            race_instances__result=1,
            race_instances__race__championship=self.championship
        ).annotate(
            win_count=Count('race_instances__result'),
        ).order_by('-win_count')

        context['sprint_winners'] = Driver.objects.filter(
            race_instances__sprint=1,
            race_instances__race__championship=self.championship
        ).annotate(
            win_count=Count('race_instances__sprint'),
        ).order_by('-win_count')

        context['podium_holders'] = Driver.objects.filter(
            race_instances__result__in=[1, 2, 3],
            race_instances__race__championship=self.championship
        ).annotate(
            win_count=Count('race_instances__result'),
        ).order_by('-win_count')

        context['pole_sitters'] = Driver.objects.filter(
            race_instances__grid=1,
            race_instances__race__championship=self.championship
        ).annotate(
            win_count=Count('race_instances__grid'),
        ).order_by('-win_count')

        context['fastest_laps'] = Driver.objects.filter(
            race_instances__fastest_lap=True,
            race_instances__race__championship=self.championship
        ).annotate(
            win_count=Count('race_instances__fastest_lap'),
        ).order_by('-win_count')

        context["race_driver_dict"] = race_driver_dict
        context["championship"] = self.championship
        context["race_list"] = race_list
        context["tabs"] = {
            "race_point": "Puan",
            "qualy": "Sıralama",
            "grid_sprint": "Sprint Grid",
            "sprint": "Sprint",
            "grid": "Grid",
            "result": "Yarış",
        }
        return context


class SeasonSupergridView(ListView):
    template_name = "fantasy/season_supergrid.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_queryset(self):
        return RaceDriver.objects.select_related(
            "driver",
            "race",
            "race__championship",
            "championship_constructor"
        ).filter(
            race__championship=self.championship
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race_list = Race.objects.select_related("championship").prefetch_related("driver_instances").filter(
            championship=self.championship
        ).order_by("round")

        race_driver_dict = {}
        supergrid_dict = {}
        race_dict = {}
        for race in race_list:
            race_dict[race] = race.best_qualifying_time()

        for rd in self.get_queryset():
            best = race_dict[rd.race]
            mine = rd.best_session_time()
            if best is None or mine is None:
                continue
            ratio = (mine / best) - 1
            if rd.driver in race_driver_dict:
                race_driver_dict[rd.driver].append(ratio)
            else:
                race_driver_dict[rd.driver] = [ratio]

        for driver, ratios in race_driver_dict.items():
            sorted_ratios = sorted(ratios)
            mean_value = mean(sorted_ratios) if sorted_ratios else None
            median_value = median(sorted_ratios) if sorted_ratios else None

            eligible_for_stat = len(sorted_ratios) > race_list.count() // 3
            first_80_percent_index = int(len(sorted_ratios) * 0.8)
            first_80_percent = sorted_ratios[1:first_80_percent_index + 1]
            trimmed_interval = sorted_ratios[round(len(sorted_ratios) * 0.125): round(len(sorted_ratios) * 0.875)]

            if first_80_percent and eligible_for_stat:  # Check if the sliced list is not empty
                mean_first_80_percent = mean(first_80_percent)
            else:
                mean_first_80_percent = None

            if trimmed_interval and eligible_for_stat:  # Check if the sliced list is not empty
                trimmed_mean = mean(trimmed_interval)
            else:
                trimmed_mean = None
            supergrid_dict[driver] = [
                f"{mean_first_80_percent:.3%}" if mean_first_80_percent is not None else None,
                f"{mean_value:.3%}" if mean_value is not None else None,
                f"{median_value:.3%}" if median_value is not None else None,
                f"{trimmed_mean:.3%}" if trimmed_mean is not None else None,
            ]
        context["race_driver_dict"] = race_driver_dict
        context["supergrid_dict"] = supergrid_dict
        context["championship"] = self.championship
        context["tabs"] = {
            "supergrid": "Süpergrid",
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
        if race_results.exists():
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
        if race_results.exists():
            context["first_race"] = race_results.earliest("race__datetime").race
            context["last_race"] = race_results.latest("race__datetime").race
            context["race_results"] = race_results.order_by("race__datetime")
        context["race_results_dict"] = race_results_dict
        context["tabs"] = {
            "result": "Yarış",
            "grid": "Grid",
            "qualy": "Sıralama",
            "grid_sprint": "Sprint Grid",
            "sprint": "Sprint",
        }

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


class StatsForSeriesView(TemplateView):
    template_name = "fantasy/stats_series.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.series = self.kwargs.get('series')
        self.series_display = f"Formula {self.series[-1]}"

        if not Championship.objects.filter(series=self.series).exists():
            raise Http404("Series not provided")


class StatsForDriverTemplateView(TemplateView):
    template_name = "fantasy/stats_drivers.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.series = self.kwargs.get('series')
        self.series_display = f"Formula {self.series[-1]}"

        if not Championship.objects.filter(series=self.series).exists():
            raise Http404("Series not provided")


class StatsForDriverView(ListView):
    allow_empty = False
    model = Driver

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.series = self.kwargs.get('series')
        self.series_display = f"Formula {self.series[-1]}"

        if not Championship.objects.filter(series=self.series).exists():
            raise Http404("Series not provided")

        # Get query parameters from the URL
        first_race = Race.objects.select_related('championship').filter(
            championship__series=self.kwargs.get('series')
        ).earliest('datetime')
        last_race = Race.objects.select_related('championship').filter(
            championship__series=self.kwargs.get('series'),
            datetime__lte=timezone.now()
        ).latest('datetime')

        start_year = int(self.request.GET.get('from_year', first_race.championship.year))
        end_year = int(self.request.GET.get('to_year', last_race.championship.year))

        try:
            first_race = Race.objects.select_related('championship').filter(
                championship__series=self.kwargs.get('series'),
                championship__year=start_year,
            ).earliest('datetime')
            last_race = Race.objects.select_related('championship').filter(
                championship__series=self.kwargs.get('series'),
                championship__year=end_year,
                datetime__lte=timezone.now()
            ).latest('datetime')
        except Race.DoesNotExist:
            raise Http404("Start year or end year parameter is invalid.")

        start_round = int(self.request.GET.get('from_round', first_race.round))
        end_round = int(self.request.GET.get('to_round', last_race.round))

        # Get Race objects for the starting and ending races
        self.start_race = get_object_or_404(
            Race,
            championship__series=self.kwargs.get('series'),
            championship__year=start_year,
            round=start_round
        )
        self.end_race = get_object_or_404(
            Race,
            championship__series=self.kwargs.get('series'),
            championship__year=end_year,
            round=end_round
        )

class StatsForDriverWinView(StatsForDriverView):
    template_name = "fantasy/stats_drivers_most_wins.html"

    def get_queryset(self):
        return Driver.objects.filter(
            race_instances__result=1,
            race_instances__race__championship__series=self.kwargs.get('series'),
            race_instances__race__datetime__gte=self.start_race.datetime,
            race_instances__race__datetime__lte=self.end_race.datetime,
        ).annotate(
            win_count=Count('race_instances__result'),
            first_win=Max('race_instances__race__datetime')
        ).order_by('-win_count', 'first_win')


class StatsForDriverPoleView(StatsForDriverView):
    template_name = "fantasy/stats_drivers_most_poles.html"

    def get_queryset(self):
        return Driver.objects.filter(
            race_instances__grid=1,
            race_instances__race__championship__series=self.kwargs.get('series'),
            race_instances__race__datetime__gte=self.start_race.datetime,
            race_instances__race__datetime__lte=self.end_race.datetime,
        ).annotate(
            pole_count=Count('race_instances__grid'),
            first_pole=Max('race_instances__race__datetime')
        ).order_by('-pole_count', 'first_pole')


class StatsForDriverPodiumView(StatsForDriverView):
    template_name = "fantasy/stats_drivers_most_podiums.html"

    def get_queryset(self):
        return Driver.objects.filter(
            race_instances__result__in=[1, 2, 3],
            race_instances__race__championship__series=self.kwargs.get('series'),
            race_instances__race__datetime__gte=self.start_race.datetime,
            race_instances__race__datetime__lte=self.end_race.datetime,
        ).annotate(
            podium_count=Count('race_instances__result'),
            first_podium=Max('race_instances__race__datetime')
        ).order_by('-podium_count', 'first_podium')


class StatsForDriverRaceView(StatsForDriverView):
    template_name = "fantasy/stats_drivers_most_races.html"

    def get_queryset(self):
        return Driver.objects.filter(
            race_instances__race__championship__series=self.kwargs.get('series'),
            race_instances__race__datetime__gte=self.start_race.datetime,
            race_instances__race__datetime__lte=self.end_race.datetime,
        ).annotate(
            race_count=Count('race_instances'),
            first_race=Max('race_instances__race__datetime')
        ).order_by('-race_count', 'first_race')


class StatsForDriverWithoutWinView(StatsForDriverView):
    template_name = "fantasy/stats_drivers_most_races_without_win.html"

    def get_queryset(self):
        return Driver.objects.filter(
            race_instances__race__championship__series=self.kwargs.get('series'),
            race_instances__race__datetime__gte=self.start_race.datetime,
            race_instances__race__datetime__lte=self.end_race.datetime,
        ).exclude(
            race_instances__result=1,
        ).annotate(
            race_count=Count('race_instances'),
            first_race=Max('race_instances__race__datetime')
        ).order_by('-race_count', 'first_race')


class StatsForDriverFinishedView(StatsForDriverView):
    template_name = "fantasy/stats_drivers_most_finished.html"

    def get_queryset(self):
        return Driver.objects.filter(
            race_instances__race__championship__series=self.kwargs.get('series'),
            race_instances__race__datetime__gte=self.start_race.datetime,
            race_instances__race__datetime__lte=self.end_race.datetime,
        ).annotate(
            race_count=Count('race_instances__result'),
            first_race=Max('race_instances__race__datetime')
        ).order_by('-race_count', 'first_race')


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

class LastRaceFantasyRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )
        latest_race = championship.latest_race()

        if latest_race:
            return latest_race.get_fantasy_url()
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
        pole_time = race.pole_time()
        race_driver_list = race.driver_instances.prefetch_related("race__driver_instances").select_related(
            "championship_constructor", "championship_constructor__constructor", "driver", "race", "race__championship"
        )
        for race_driver in race_driver_list:
            race_driver.pole_margin = None
            race_driver.pole_ratio = None
            qualifying_time = race_driver.qualifying_time()
            if pole_time and qualifying_time:
                race_driver.pole_margin = f"{qualifying_time - pole_time:.3f}"
                race_driver.pole_ratio = f"{qualifying_time / pole_time - 1:.3%}"

        context["race_driver_list"] = race_driver_list
        context["opts"] = race._meta
        context["tabs"] = {
            "quali": "Sıralama Turları",
            "race": "Yarış",
            "sprint": "Sprint",
            "sprint_quali": "Sprint Sıralama",
        }
        return context

class RaceFantasyView(DetailView):
    model = Race
    template_name = "fantasy/race_fantasy_detail.html"

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
        context["opts"] = race._meta
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
        return self.championship.races.select_related("circuit", "rating_instance").order_by("round")


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
        if not self.championship.is_fantasy:
            raise Http404("Fantasy Lig bu şampiyona için kapalıdır.")

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
        table_rows = race_count + 4
        latest_race_round = 0

        race_team_dict = {user: [None] * table_rows for user in user_list}
        for rt in self.get_queryset():
            race_team_dict[rt.user][rt.race.round - 1 + 4] = rt
            if rt.race.round >= latest_race_round:
                latest_race_round = rt.race.round
                race_team_dict[rt.user][0] = rt
                race_team_dict[rt.user][1] = rt
                race_team_dict[rt.user][2] = rt

        if self.request.user.is_authenticated:
            team_count = RaceTeam.objects.filter(
                user=self.request.user,
                race__championship=self.championship
            ).count()
        else:
            team_count = None

        context = super().get_context_data(**kwargs)
        context["race_team_count"] = team_count
        context["race_list"] = race_list
        context["race_team_dict"] = race_team_dict
        context["tabs"] = {
            "total_point": "Toplam Puan",
        }
        return context


class FantasyProfileRedirectView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse(
            "formula:team_detail",
            kwargs={
                'series': self.kwargs.get("series"),
                'year': self.kwargs.get("year"),
                'username': self.request.user.username
            }
        )


class FantasyUserProfileView(ListView):
    template_name = "fantasy/fantasy_user_profile.html"
    allow_empty = False

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
        if not self.championship.is_fantasy:
            raise Http404("Fantasy Lig bu şampiyona için kapalıdır.")

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
        if not self.championship.is_fantasy:
            raise Http404("Fantasy Lig bu şampiyona için kapalıdır.")

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
        return self.request.user.is_superuser
