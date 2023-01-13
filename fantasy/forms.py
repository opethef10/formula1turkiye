from django import forms
from .models import *

BEGINNING_TOKEN = 32
STARTING_BUDGET = 55
MAX_DRIVERS_IN_A_TEAM = 8


class RaceDriverMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, racedriver):
        return f"{racedriver.driver}: {racedriver.price}₺"


class CheckboxSelectMultipleWithPrice(forms.CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option['attrs']['price'] = value.instance.price
        return option


class TeamCreateUpdateForm(forms.ModelForm):
    budget = forms.CharField(disabled=True, required=False)
    token = forms.IntegerField(disabled=True, required=False, initial=BEGINNING_TOKEN)
    race_drivers = RaceDriverMultipleChoiceField(
        queryset=RaceDriver.objects.filter(
            race=Race.objects.get(
                championship__slug="2022-f1",
                round=1
            )
        ).order_by(
            "championship_constructor__garage_order"
        ),
        widget=CheckboxSelectMultipleWithPrice(),
        help_text="En fazla 8 pilot seçebilirsiniz."
    )

    class Meta:
        model = RaceTeam
        fields = ["tactic", "token", "budget", "race_drivers"]

    def clean(self):
        cleaned_data = super().clean()
        race_drivers = self.cleaned_data.get('race_drivers')
        if race_drivers is None:
            raise forms.ValidationError("You should select at least one driver")
        if len(race_drivers) > MAX_DRIVERS_IN_A_TEAM:
            raise forms.ValidationError("You cannot select more than 8 drivers")

        total_price = sum(race_driver.price for race_driver in race_drivers)
        left_budget = STARTING_BUDGET - total_price
        if left_budget < 0:
            raise forms.ValidationError("Budget left can't be negative")
        cleaned_data['budget'] = left_budget
        cleaned_data['token'] = BEGINNING_TOKEN
        return cleaned_data
