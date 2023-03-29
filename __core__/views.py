from django.conf import settings
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import TemplateView

from fantasy.models import Championship, Race

HOURS = settings.HOURS


@method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        for championship in Championship.objects.filter(year=2023):
            prev_race_fantasy = championship.races.filter(
                deadline__lt=timezone.now()
            ).latest("deadline")
            prev_race_tahmin = championship.races.filter(
                datetime__lt=timezone.now()
            ).latest("datetime")
            context[f"last_race_fantasy_f{championship.series[-1]}"] = prev_race_fantasy
            context[f"last_race_tahmin_f{championship.series[-1]}"] = prev_race_tahmin
            if user.is_authenticated:
                context[f"is_fantasy_team_f{championship.series[-1]}"] = bool(championship.teams.filter(user=user))
        return context
