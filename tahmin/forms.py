from django import forms
from .models import *


class RaceDriverChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, racedriver):
        return racedriver.driver


class NewTahminForm(forms.ModelForm):
    class Meta:
        model = RaceTahmin
        exclude = ["race", "user"]

    def __init__(self, current_race, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for idx in range(1, 11):
            self.fields[f"prediction_{idx}"] = RaceDriverChoiceField(
                label=f"{idx}. Sürücü",
                queryset=RaceDriver.objects.filter(
                    race=current_race
                ).order_by(
                    "championship_constructor__garage_order",
                    "driver__number"
                )
            )
        self.fields["question_1"].label = "11. Soru henüz oluşturulmadı"
        self.fields["question_1"].disabled = True
        self.fields["question_2"].label = "12. Soru henüz oluşturulmadı"
        self.fields["question_2"].disabled = True

        for idx, question in enumerate(current_race.questions.all()[:2], 1):
            self.fields[f"question_{idx}"] = forms.ChoiceField(
                label=f"1{idx}. {question.form_str()}",
                widget=forms.RadioSelect,
                choices=QUESTION_CHOICES[:4 if question.choice_D else (3 if question.choice_C else 2)],
            )
