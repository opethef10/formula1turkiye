from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import FormView

from .forms import DynamicPredictionForm
from .models import Prediction, Answer, Question
from f1t.apps.fantasy.models import Championship, Driver, Race, Constructor

User = get_user_model()


class PredictionListView(ListView):
    template_name = 'season_predictions/list.html'
    context_object_name = 'predictions'
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
        return Prediction.objects.filter(
            championship=self.championship
        ).select_related('user').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['championship'] = self.championship
        return context


class PredictionDetailView(DetailView):
    model = Prediction
    template_name = 'season_predictions/detail.html'
    context_object_name = 'prediction'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Fetch the championship object
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_object(self):
        user = get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )
        return get_object_or_404(
            Prediction,
            user=user,
            championship=self.championship
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prediction = self.object
        processed_answers = []

        for answer in prediction.answers.all():
            answer_data = {
                'question': answer.question,
                'value': answer.value,
                'resolved_value': None
            }

            # Resolve IDs to actual objects
            if answer.question.question_type in ['driver_singleselect', 'driver_multiselect']:
                if isinstance(answer.value, list):
                    answer_data['resolved_value'] = Driver.objects.filter(id__in=answer.value)
                else:
                    answer_data['resolved_value'] = Driver.objects.filter(id=answer.value).first()

            elif answer.question.question_type in ['constructor_singleselect', 'constructor_multiselect']:
                if isinstance(answer.value, list):
                    answer_data['resolved_value'] = Constructor.objects.filter(id__in=answer.value)
                else:
                    answer_data['resolved_value'] = Constructor.objects.filter(id=answer.value).first()

            elif answer.question.question_type in ['race_singleselect', 'race_select']:
                if isinstance(answer.value, list):
                    answer_data['resolved_value'] = Race.objects.filter(id__in=answer.value)
                else:
                    answer_data['resolved_value'] = Race.objects.filter(id=answer.value).first()
            elif answer.question.question_type == 'driver_matrix':
                answer_data['resolved_value'] = []
                for driver_id in answer.value:
                    driver = Driver.objects.filter(id=driver_id).first()
                    answer_data['resolved_value'].append(driver)

            processed_answers.append(answer_data)

        context['processed_answers'] = processed_answers
        return context


class PredictionFormView(LoginRequiredMixin, FormView):
    template_name = 'season_predictions/form.html'
    form_class = DynamicPredictionForm
    success_url = reverse_lazy('django.contrib.flatpages.views.flatpage', args=["season_sent/"])

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Fetch the championship object
        self.championship = get_object_or_404(
            Championship,
            series=self.kwargs.get("series"),
            year=self.kwargs.get("year")
        )

    def get_form_kwargs(self):
        # Pass the championship to the form
        kwargs = super().get_form_kwargs()
        kwargs['championship'] = self.championship
        return kwargs

    def form_valid(self, form):
        # Get or create prediction (only one per user/championship)
        prediction, created = Prediction.objects.update_or_create(
            user=self.request.user,
            championship=self.championship,
            defaults={
                # Explicitly update updated_at even if no other fields change
                'updated_at': timezone.now()
            }
        )

        # Delete existing answers before creating new ones
        prediction.answers.all().delete()

        # Create new answers
        for question in Question.objects.filter(championship=self.championship, active=True):
            field_name = f'q_{question.id}'
            if question.question_type == 'driver_matrix':
                # Collect all position values
                matrix_values = [
                    form.cleaned_data.get(f'q_{question.id}_pos_{pos}')
                    for pos in range(1, question.positions + 1)
                ]
                value = matrix_values
            else:
                value = form.cleaned_data.get(field_name)

            if value:
                Answer.objects.create(
                    prediction=prediction,
                    question=question,
                    value=value
                )

        # Force save to update the timestamp (even if no other fields changed)
        prediction.save()

        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        try:
            prediction = Prediction.objects.get(
                user=self.request.user,
                championship=self.championship
            )
            for answer in prediction.answers.all():
                if answer.question.question_type == 'driver_matrix':
                    # For matrix questions, populate position fields
                    for idx, driver_id in enumerate(answer.value, start=1):
                        initial[f'q_{answer.question.id}_pos_{idx}'] = driver_id
                else:
                    # Regular question handling
                    initial[f'q_{answer.question.id}'] = answer.value
        except Prediction.DoesNotExist:
            pass
        return initial
