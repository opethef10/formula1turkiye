from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from f1t.apps.fantasy.models import Championship
from .models import Rating


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
        return Rating.objects.select_related('race', 'race__championship').filter(
            race__championship=self.championship
        )

class SeriesRatingView(ListView):
    allow_empty = False
    template_name = "ratings/series_ratings.html"
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
