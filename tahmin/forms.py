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
            self.fields[f"prediction_{idx}"] = RaceDriverChoiceField(queryset=RaceDriver.objects.filter(
                        race=current_race
                    ).order_by(
                        "championship_constructor__garage_order",
                        "driver__number"
                    )
            )
