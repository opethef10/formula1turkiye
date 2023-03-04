from django import forms
from .models import *


class RaceDriverChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, racedriver):
        return racedriver.driver


class NewTahminForm(forms.ModelForm):
    class Meta:
        model = RaceTahmin
        exclude = ["race", "team"]

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
            self.fields["question_1"] = forms.ChoiceField(
                label=(
                    "11. Podyuma Red Bull veya Ferrari pilotlarından başka çıkan olur mu?\n\n"
                    "A) Evet [90 puan]\n"
                    "B) Hayır [60 puan]"
                ),
                widget=forms.RadioSelect,
                choices=QUESTION_CHOICES[:2],
            )
            self.fields["question_2"] = forms.ChoiceField(
                label=(
                    "12. Albon, Tsunoda, Gasly üçlüsünden hangisi yarışı önde tamamlar?\n\n"
                    "A) Albon [60 puan]\n"
                    "B) Tsunoda [60 puan]\n"
                    "C) Gasly [65 puan]"
                ),
                widget=forms.RadioSelect,
                choices=QUESTION_CHOICES,
            )
