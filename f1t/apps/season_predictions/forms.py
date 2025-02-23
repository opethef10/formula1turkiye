from django import forms

from f1t.apps.fantasy.models import Driver, Race, Constructor
from .models import Question


class DynamicPredictionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.championship = kwargs.pop('championship', None)
        super().__init__(*args, **kwargs)

        # Filter active questions by championship
        self.active_questions = Question.objects.filter(
            championship=self.championship,
            active=True
        ).order_by('order')

        drivers = Driver.objects.filter(race_instances__race__championship=self.championship).distinct()
        races = Race.objects.filter(championship=self.championship)
        constructors = Constructor.objects.filter(championship=self.championship)

        for question in self.active_questions:
            field_kwargs = {
                'label': f"{question.order}. {question.text}",
                'help_text': question.help_text,
                'required': True
            }

            if question.question_type == 'integer':
                self.fields[f'q_{question.id}'] = forms.IntegerField(
                    **field_kwargs,
                    min_value=question.validation_min,
                    max_value=question.validation_max
                )
            elif question.question_type == 'multiple_choice':
                choices = [(c.strip(), c.strip()) for c in question.choices.split(',')]
                self.fields[f'q_{question.id}'] = forms.MultipleChoiceField(
                    **field_kwargs,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple
                )
            elif question.question_type == 'single_choice':
                choices = [(c.strip(), c.strip()) for c in question.choices.split(',')]
                self.fields[f'q_{question.id}'] = forms.ChoiceField(
                    **field_kwargs,
                    choices=choices,
                    widget=forms.RadioSelect
                )
            elif question.question_type == 'driver_multiselect':
                choices = [(d.id, d.name) for d in drivers]
                self.fields[f'q_{question.id}'] = forms.MultipleChoiceField(
                    **field_kwargs,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple
                )
            elif question.question_type == 'driver_singleselect':
                choices = [(driver.id, driver.name) for driver in drivers]
                self.fields[f'q_{question.id}'] = forms.ChoiceField(
                    **field_kwargs,
                    choices=choices,
                    widget=forms.RadioSelect
                )
            elif question.question_type == 'race_select':
                choices = [(race.id, race.name) for race in races]
                self.fields[f'q_{question.id}'] = forms.MultipleChoiceField(
                    **field_kwargs,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple
                )
            elif question.question_type == 'race_singleselect':
                choices = [(race.id, race.name) for race in races]
                self.fields[f'q_{question.id}'] = forms.ChoiceField(
                    **field_kwargs,
                    choices=choices,
                    widget=forms.RadioSelect
                )
            elif question.question_type == 'constructor_singleselect':
                choices = [(constructor.id, constructor.name) for constructor in constructors]
                self.fields[f'q_{question.id}'] = forms.ChoiceField(
                    **field_kwargs,
                    choices=choices,
                    widget=forms.RadioSelect
                )
            elif question.question_type == 'constructor_multiselect':
                choices = [(constructor.id, constructor.name) for constructor in constructors]
                self.fields[f'q_{question.id}'] = forms.MultipleChoiceField(
                    **field_kwargs,
                    choices=choices,
                    widget=forms.CheckboxSelectMultiple
                )
            elif question.question_type == 'text':
                self.fields[f'q_{question.id}'] = forms.CharField(
                    **field_kwargs,
                    widget=forms.Textarea
                )
            elif question.question_type == 'boolean':
                self.fields[f'q_{question.id}'] = forms.TypedChoiceField(
                    **field_kwargs,
                    choices=[(True, 'Evet'), (False, 'Hayır')],
                    coerce=lambda x: x == 'True',  # Convert string to boolean
                    widget=forms.RadioSelect,
                    empty_value=None,
                )
            elif question.question_type == 'driver_matrix':
                # Add hidden field for question text
                self.fields[f'q_{question.id}_header'] = forms.CharField(
                    label=f"{question.order}. {question.text}",
                    initial=question.positions,
                    widget=forms.HiddenInput(),
                    required=False
                )
                # Create fields based on the question's positions
                for position in range(1, question.positions + 1):
                    self.fields[f'q_{question.id}_pos_{position}'] = forms.ChoiceField(
                        label=f"{position}. Sıra",
                        choices=[('', '----')] + [(d.id, d.name) for d in drivers],
                        required=True,
                        widget=forms.Select(attrs={
                            'class': 'form-select',
                            'data-question-id': question.id,
                            'data-position': position
                        })
                    )
                if question.help_text:
                    self.fields[f'q_{question.id}_header'].help_text = question.help_text

    def clean(self):
        cleaned_data = super().clean()

        # Check for duplicate drivers in matrix questions
        for question in self.active_questions.filter(question_type='driver_matrix'):
            positions = question.positions
            driver_positions = {}
            duplicate_errors = []

            # Collect all selected drivers and their positions
            for pos in range(1, positions + 1):
                field_name = f'q_{question.id}_pos_{pos}'
                driver_id = cleaned_data.get(field_name)

                if driver_id:
                    driver = Driver.objects.filter(id=driver_id).first()
                    driver_name = driver.name if driver else "Silinmiş Pilot"

                    if driver_id in driver_positions:
                        driver_positions[driver_id]['positions'].append(pos)
                    else:
                        driver_positions[driver_id] = {
                            'name': driver_name,
                            'positions': [pos]
                        }

            # Check for duplicates and prepare errors
            for driver_id, data in driver_positions.items():
                if len(data['positions']) > 1:
                    for pos in data['positions']:
                        field_name = f'q_{question.id}_pos_{pos}'
                        error_msg = (
                            f"{data['name']} birden fazla sıraya yerleştirilemez! "
                            f"(Aynı pilot {len(data['positions'])} kez seçilmiş)"
                        )
                        duplicate_errors.append((field_name, error_msg))

            # Add errors to specific fields
            for field_name, error_msg in duplicate_errors:
                self.add_error(
                    field_name,
                    forms.ValidationError(
                        error_msg,
                        code='duplicate_driver'
                    )
                )

        return cleaned_data
