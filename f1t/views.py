from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import mail_admins
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.generic import FormView, TemplateView

from f1t.apps.fantasy.models import Championship, Race
from .forms import ContactForm

HOURS = settings.HOURS


# @method_decorator([vary_on_cookie, cache_page(24 * HOURS)], name='dispatch')
class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        for championship in Championship.objects.filter(year=2023):
            team = None
            team_count = None
            if user.is_authenticated:
                team = user.teams.filter(championship=championship).first()
                if team is None:
                    team_count = 0
                else:
                    team_count = team.race_instances.count()
            context[f"fantasy_team_{championship.series}"] = team
            context[f"race_team_count_{championship.series}"] = team_count

        return context


class ContactView(SuccessMessageMixin, FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_message = "Mesajınız başarıyla gönderildi!"
    success_url = reverse_lazy('contact')
    subject = "Bize Ulaşın!"

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user  # Get the currently logged-in user

        # Check if the user is authenticated and populate the initial data
        if user.is_authenticated:
            initial['first_name'] = user.first_name
            initial['last_name'] = user.last_name
            initial['email'] = user.email

        return initial

    def form_valid(self, form):
        body = [
            form.cleaned_data['first_name'],
            form.cleaned_data['last_name'],
            form.cleaned_data['email'],
        ]
        mail_admins(
            subject=f"{self.subject} - {body[0].strip()} {body[1].strip()} - {body[2].strip()}",
            message=form.cleaned_data['message'].strip()
        )
        return super().form_valid(form)
