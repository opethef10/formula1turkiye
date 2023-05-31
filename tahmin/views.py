import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import ListView, TemplateView, UpdateView

from .forms import NewTahminForm
from .models import Tahmin, tahmin_score
from fantasy.models import Championship, Race

logger = logging.getLogger("f1tform")
HOURS = settings.HOURS


@method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class ChampionshipListView(ListView):
    queryset = Championship.objects.filter(is_tahmin=True)
    ordering = ["-year", "series"]
    template_name = "tahmin/championship_list.html"


# @method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class RaceListView(ListView):
    template_name = "tahmin/race_list.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )

    def get_queryset(self):
        return self.championship.races.only("name", "round", "championship", "datetime")


# @method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
class RaceTahminView(ListView):
    template_name = "tahmin/race_tahmins.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        self.race = get_object_or_404(
            Race.objects.prefetch_related(
                "questions", "driver_instances", "tahmins", "driver_instances__driver"
            ).select_related("championship"),
            championship=self.championship,
            round=self.kwargs.get('round')
        )

    def get_queryset(self):
        return self.race.tahmins.select_related(
            "user",
            *(f"prediction_{idx}" for idx in range(1, 11)),
            *(f"prediction_{idx}__driver" for idx in range(1, 11))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tahmin_counts"] = [
            race_driver.tahmin_count(position)
            for position, race_driver
            in enumerate(self.race.top10, 1)
        ]
        context["tahmin_points"] = [tahmin_score(count) for count in context["tahmin_counts"]]
        context["race"] = self.race
        context["before_race"] = self.race.datetime > timezone.now()
        return context


# @method_decorator([vary_on_cookie, cache_page(12 * HOURS)], name='dispatch')
class TeamListView(ListView):
    model = Tahmin
    template_name = "tahmin/team_list.html"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )

    def get_queryset(self):
        return Tahmin.objects.prefetch_related(
            *(f"prediction_{idx}__driver" for idx in range(1, 11)),
            "race__tahmins", "race__questions",
            "race__driver_instances",
            *(f"race__driver_instances__prediction_{idx}" for idx in range(1, 11)),
            "race__championship",
        ).select_related(
            "user",
            "race",
            *(f"prediction_{idx}" for idx in range(1, 11)), *(f"prediction_{idx}__driver" for idx in range(1, 11))
        ).filter(
            race__championship=self.championship
        )

    def get_context_data(self, **kwargs):
        race_list = Race.objects.select_related("championship").prefetch_related(
            "tahmins",
            "questions", "driver_instances", "driver_instances__driver"
        ).filter(
            championship=self.championship
        )
        race_count = race_list.count()
        tahmin_list = self.get_queryset()
        tahmin_race_user_matrix = {}
        for tahmin in tahmin_list:
            if tahmin.user not in tahmin_race_user_matrix:
                tahmin_race_user_matrix[tahmin.user] = [None] * race_count
            tahmin_race_user_matrix[tahmin.user][tahmin.race.round - 1] = tahmin

        context = super().get_context_data(**kwargs)
        context["championship"] = self.championship
        context["race_list"] = race_list
        context["tahmin_race_user_matrix"] = tahmin_race_user_matrix
        context["tabs"] = {
            "total_point": "Toplam Puan",
        }
        return context


class NewTahminView(LoginRequiredMixin, UpdateView):
    form_class = NewTahminForm
    success_url = "/sent/"
    template_name = "tahmin/tahmin_form.html"
    error_message = "Form gönderilemedi, form hatalarını düzelttikten sonra tekrar deneyin!"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            slug=self.kwargs.get('champ')
        )
        self.race = self.championship.next_race("tahmin")

    def get(self, request, *args, **kwargs):
        if self.race is None:
            return TemplateView.as_view(template_name='expired.html')(request, *args, **kwargs)
        else:
            return super().get(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['current_race'] = self.race
        return kwargs

    def get_object(self):
        try:
            return Tahmin.objects.get(
                user=self.request.user,
                race=self.race
            )
        except Tahmin.DoesNotExist:
            return

    def form_valid(self, form):
        form.instance.race = self.race
        form.instance.user = self.request.user
        response = super().form_valid(form)

        for key, value in form.cleaned_data.items():
            if key.startswith("prediction"):
                form.cleaned_data[key] = str(value.driver)
        logger.info(f"TAHMİN: {self.request.user.get_full_name()}: {form.cleaned_data}")
        return response

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, self.error_message)
        for key, value in form.cleaned_data.items():
            if key.startswith("prediction"):
                form.cleaned_data[key] = str(value.driver)
        logger.warning(f"TAHMİN: {self.request.user.get_full_name()}: {form.cleaned_data} ERRORS: {form.errors!r}")
        return response
