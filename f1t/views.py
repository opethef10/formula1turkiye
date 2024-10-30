from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMessage
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
        current_year = timezone.now().year
        for championship in Championship.objects.filter(year=current_year):
            fantasy_instances = None
            team_count = None
            if user.is_authenticated:
                fantasy_instances = user.fantasy_instances.filter(race__championship=championship)
                if fantasy_instances is None:
                    team_count = 0
                else:
                    team_count = fantasy_instances.count()
            context[f"fantasy_team_{championship.series}"] = user.username if fantasy_instances else None
            context[f"race_team_count_{championship.series}"] = team_count
        context['current_year'] = current_year

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
        first_name, last_name, mail_address = [
            form.cleaned_data['first_name'].strip(),
            form.cleaned_data['last_name'].strip(),
            form.cleaned_data['email'].strip(),
        ]

        # Use EmailMessage instead of send_mail
        admin_emails = [email for name, email in settings.ADMINS]  # Extract emails from ADMINS

        email = EmailMessage(
            subject=f"{settings.EMAIL_SUBJECT_PREFIX}{self.subject} - {first_name} {last_name}",
            body=form.cleaned_data['message'].strip(),
            from_email=None,  # You can specify a from address here if needed
            to=admin_emails,  # Use the admin emails from settings.
            reply_to=[mail_address]
        )

        # Send the email
        email.send(fail_silently=False)
        return super().form_valid(form)
