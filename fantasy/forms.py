from django import forms
from .models import *


class RaceDriverMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, racedriver):
        return f"{racedriver.driver.code}: {racedriver.price}₺"


class PriceSelect(forms.CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option['attrs']['price'] = value.instance.price
        return option


class TeamCreateForm(forms.ModelForm):
    budget = forms.FloatField(disabled=True, required=False)
    drivers = RaceDriverMultipleChoiceField(
        queryset=RaceDriver.objects.filter(
            race=Race.objects.get(
                championship__slug="2022-f1",
                round=1
            )
        ),
        widget=PriceSelect
    )

    class Meta:
        model = RaceTeam
        fields = ["tactic", "budget"]

    def clean(self):
        cleaned_data = super().clean()
        drivers = self.cleaned_data.get('drivers')
        if drivers is None:
            raise forms.ValidationError("You should select at least one driver")
        if len(drivers) > 8:
            raise forms.ValidationError("You cannot select more than 8 drivers")
        total_price = sum(driver.price for driver in drivers)
        BUDGET = 55
        left_budget = BUDGET - total_price
        if left_budget < 0:
            raise forms.ValidationError("Budget left can't be negative")
        cleaned_data['budget'] = left_budget
        return cleaned_data
