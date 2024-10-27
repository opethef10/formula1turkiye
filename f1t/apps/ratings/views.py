from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.urls import reverse

from f1t.apps.fantasy.models import Championship, Race, RaceDriver
from .models import Rating
from .forms import RatingForm

# Prefetch only the RaceDriver instances with result=1 (i.e., the winners)
winner_prefetch = Prefetch(
    'driver_instances',  # The many-to-many field name
    queryset=RaceDriver.objects.select_related(
        'driver', 'championship_constructor', 'championship_constructor__constructor'
    ).filter(result=1),
    to_attr='prefetched_winners'  # This attaches the winners to each Race as `prefetched_winners`
)

class SeasonRatingView(ListView):
    allow_empty = False
    template_name = "ratings/season_ratings.html"
    model = Rating

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_queryset(self):
        return Race.objects.prefetch_related(winner_prefetch).select_related(
            'rating_instance', 'championship'
        ).filter(championship=self.championship, rating_instance__gt=0)


class SeriesRatingView(ListView):
    allow_empty = False
    template_name = "ratings/series_ratings.html"
    model = Rating

    def get_queryset(self):
        return Race.objects.prefetch_related(winner_prefetch).select_related(
            'rating_instance', 'championship'
        ).filter(championship__series=self.kwargs.get("series"), rating_instance__gt=0)

    def get_context_data(self):
        context = super().get_context_data()
        context["series"] = self.kwargs.get('series')
        context["series_display"] = f"Formula {self.kwargs.get('series')[-1]}"
        return context


class RatingCreateView(SuccessMessageMixin, UserPassesTestMixin, UpdateView):
    model = Rating
    form_class = RatingForm
    success_message = "Yarış puanı başarıyla güncellendi!"

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.race = get_object_or_404(
            Race,
            championship__series=self.kwargs.get("series"),
            championship__year=self.kwargs.get("year"),
            round=self.kwargs.get("round")
        )

    def get_object(self):
        try:
            return Rating.objects.get(race=self.race)
        except Rating.DoesNotExist:
            return

    def get_success_url(self):
        series = self.kwargs['series']
        year = self.kwargs['year']
        return reverse('ratings:season_ratings', kwargs={'series': series, 'year': year})

    def form_valid(self, form):
        form.instance.race = self.race
        form.instance.score = form.cleaned_data['score']
        form.instance.amount = form.cleaned_data['amount']
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

