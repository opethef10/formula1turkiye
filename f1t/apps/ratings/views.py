from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView
from django.views.generic.edit import UpdateView
from django.urls import reverse

from f1t.apps.fantasy.models import Championship, Race
from .models import Rating
from .forms import RatingForm


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
        return self.request.user.is_staff

