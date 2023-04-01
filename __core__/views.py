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
            if user.is_authenticated:
                team = user.teams.filter(championship=championship).first()
                if team is None:
                    team_count = 0
                else:
                    team_count = team.race_instances.count()
            else:
                team = None
                team_count = None
            prev_race_fantasy = championship.races.filter(
                deadline__lt=timezone.now()
            ).latest("deadline")
            prev_race_tahmin = championship.races.filter(
                datetime__lt=timezone.now()
            ).latest("datetime")
            context[f"last_race_fantasy_{championship.series}"] = prev_race_fantasy
            context[f"last_race_tahmin_{championship.series}"] = prev_race_tahmin
            context[f"fantasy_team_{championship.series}"] = team
            context[f"race_team_count_{championship.series}"] = team_count

        return context
