from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum, F, Case, When, IntegerField, Q
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView

from .models import PollResponse
from .forms import DragDropRankForm
from f1t.apps.fantasy.models import Championship, Driver, Race

User = get_user_model()
DRIVER_RANK_POINTS = [25, 18, 15, 12, 10, 8, 6, 4, 2, 1, -1, -2, -4, -6, -8, -10, -12, -15, -18, -25]


class DriverPointsView(TemplateView):
    template_name = 'driver_ranks/driver_points.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Create a Case statement to assign points based on position from PollResponse
        point_cases = Case(
            *[When(pollresponse__position=i + 1, then=DRIVER_RANK_POINTS[i]) for i in range(20)],
            default=0,
            output_field=IntegerField()
        )

        driver_points = Driver.objects.annotate(
            total_points=Sum(
                point_cases,
                filter=Q(pollresponse__championship=self.championship)
            )
        ).filter(
            total_points__isnull=False
        ).order_by('-total_points')

        context['driver_points'] = driver_points
        return context


class DragDropRankView(SuccessMessageMixin, LoginRequiredMixin, FormView):
    template_name = 'driver_ranks/drag_drop.html'
    form_class = DragDropRankForm
    success_message = "Sürücü sıralamanız başarıyla kaydedildi."

    def get_success_url(self):
        return self.request.path

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Fetch the championship object
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def _is_past_deadline(self):
        try:
            race = self.championship.races.earliest("fp1_datetime")
            deadline = race.fp1_datetime
            return timezone.now() > deadline
        except Race.DoesNotExist:
            return True

    def get(self, request, *args, **kwargs):
        if self._is_past_deadline():
            return TemplateView.as_view(template_name='expired.html')(request)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self._is_past_deadline():
            return TemplateView.as_view(template_name='expired.html')(request)
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        return Driver.objects.filter(
            race_instances__race__championship=self.championship
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        race = self.championship.races.earliest("fp1_datetime")
        # Get base queryset
        drivers = self.get_queryset()

        # Check for existing poll response
        if self.request.user.is_authenticated:
            existing_response = PollResponse.objects.filter(
                user=self.request.user,
                championship=self.championship
            ).order_by('position')

            if existing_response.exists():
                # Get driver IDs in existing order
                ordered_ids = existing_response.values_list('driver_id', flat=True)

                # Preserve the order from the existing response
                preserved_order = Case(
                    *[When(id=driver_id, then=pos) for pos, driver_id in enumerate(ordered_ids)],
                    output_field=IntegerField()
                )
                drivers = drivers.order_by(preserved_order)
        context['drivers'] = drivers
        context['deadline'] = race.fp1_datetime
        return context

    def form_valid(self, form):
        driver_ids = form.cleaned_data['ranked_drivers']
        user = self.request.user
        user.pollresponse_set.filter(
            championship=self.championship
        ).delete()

        for position, driver_id in enumerate(driver_ids, start=1):
            PollResponse.objects.create(
                user=self.request.user,
                championship=self.championship,
                driver_id=driver_id,
                position=position
            )
        return super().form_valid(form)


class DriverRanksDetailView(DetailView):
    model = PollResponse
    template_name = 'driver_ranks/detail.html'
    context_object_name = 'user'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Fetch the championship object
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )

    def _is_past_deadline(self):
        try:
            race = self.championship.races.earliest("fp1_datetime")
            deadline = race.fp1_datetime
            return timezone.now() > deadline
        except Race.DoesNotExist:
            return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        user_responses = user.pollresponse_set.select_related('driver').filter(
            championship=self.championship
        ).order_by('position')

        context['processed_answers'] = user_responses
        return context


class DriverRankListView(ListView):
    template_name = 'driver_ranks/list.html'
    context_object_name = 'users'
    allow_empty = False

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Fetch the championship object
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )
    def get_queryset(self):
        return User.objects.filter(
            pollresponse__championship=self.championship
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['championship'] = self.championship
        return context
