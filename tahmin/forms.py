from django import forms

from .models import Tahmin, QUESTION_CHOICES


class RaceDriverChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, racedriver):
        return racedriver.driver


class NewTahminForm(forms.ModelForm):
    class Meta:
        model = Tahmin
        exclude = ["race", "user"]

    def __init__(self, current_race, *args, **kwargs):
        super().__init__(*args, **kwargs)
        race_drivers = current_race.driver_instances.select_related(
            "driver"
        )
        for idx in range(1, 11):
            self.fields[f"prediction_{idx}"] = RaceDriverChoiceField(
                label=f"{idx}. Sürücü",
                queryset=race_drivers
            )
        self.fields["answer_1"].label = "11. Soru henüz oluşturulmadı"
        self.fields["answer_1"].disabled = True
        self.fields["answer_2"].label = "12. Soru henüz oluşturulmadı"
        self.fields["answer_2"].disabled = True

        for idx, question in enumerate(current_race.questions.all()[:2], 1):
            self.fields[f"answer_{idx}"] = forms.ChoiceField(
                label=f"1{idx}. {question.form_str()}",
                widget=forms.RadioSelect,
                choices=QUESTION_CHOICES[:4 if question.choice_D else (3 if question.choice_C else 2)],
            )
