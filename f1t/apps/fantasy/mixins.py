from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404

from f1t.apps.fantasy.models import Championship, Race


class ChampionshipMixin:
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )


class RaceRangeSelectorMixin(ChampionshipMixin):
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        try:
            # Get first and last races as default boundaries
            first_race = self.championship.races.earliest("datetime")
            last_race = self.championship.races.latest("datetime")
        except Race.DoesNotExist:
            raise Http404("Bu şampiyona için yarış bulunamadı.")

        # Get query parameters from the URL
        try:
            start_round = int(self.request.GET.get('from_round', first_race.round))
            end_round = int(self.request.GET.get('to_round', last_race.round))
        except ValueError:
            # If the value cannot be converted to an integer, return to defaults
            start_round = first_race.round
            end_round = last_race.round
            messages.error(request, "Hatalı parametre girdiniz. Parametrelerin tamsayı olmasına dikkat ediniz.")

        # Check if the parameters within the boundaries
        if not (first_race.round <= start_round <= last_race.round) or not (first_race.round <= end_round <= last_race.round):
            start_round = first_race.round
            end_round = last_race.round
            messages.error(request, "Hatalı parametre girdiniz. Parametreler sezondaki geçerli yarış aralığında olmalıdır.")

        # Check if 'from_round' is greater than 'to_round'
        if start_round > end_round:
            start_round = first_race.round
            end_round = last_race.round
            messages.error(request, "Hatalı seçim gerçekleştirdiniz. Sezon süzgecinde ilk yarış, son yarıştan önce olmalıdır.")

        # Get Race objects for the starting and ending races
        self.start_race = get_object_or_404(
            Race,
            championship=self.championship,
            round=start_round
        )
        self.end_race = get_object_or_404(
            Race,
            championship=self.championship,
            round=end_round
        )
