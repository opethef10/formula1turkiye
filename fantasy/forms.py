from django import forms
from .models import *

BEGINNING_TOKEN = 32
STARTING_BUDGET = 50
MAX_DRIVERS_IN_A_TEAM = 8


class RaceDriverMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, racedriver):
        return f"{racedriver.driver}: {racedriver.price}₺"


class CheckboxSelectMultipleWithPrice(forms.CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option['attrs']['price'] = value.instance.price
        return option


class NewTeamForm(forms.ModelForm):

    class Meta:
        model = RaceTeam
        fields = ["tactic", "token", "budget", "race_drivers"]

    def __init__(self, request, current_race, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["budget"] = forms.DecimalField(disabled=True, required=False)
        self.fields["token"] = forms.IntegerField(disabled=True, required=False, initial=BEGINNING_TOKEN)
        self.fields["race_drivers"] = RaceDriverMultipleChoiceField(
            queryset=RaceDriver.objects.filter(
                race=current_race
            ).order_by(
                "championship_constructor__garage_order",
                "driver__number"
            ),
            widget=CheckboxSelectMultipleWithPrice(),
            help_text="En fazla 8 pilot seçebilirsiniz."
        )

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


class EditTeamForm(forms.ModelForm):

    class Meta:
        model = RaceTeam
        fields = ["race_drivers"]

    def __init__(self, request, current_race, *args, **kwargs):
        super().__init__(*args, **kwargs)
        prev_race = current_race.get_previous_by_datetime()
        current_racedrivers = RaceDriver.objects.filter(
            race=current_race
        )
        prv_drivers = Driver.objects.filter(
            race_instances__raceteamdrivers__raceteam__team__user=request.user,
            race_instances__race=prev_race,
        )
        self.prev_race_team = RaceTeam.objects.get(
            race=prev_race,
            team__user=request.user
        )
        self.old_race_drivers = current_racedrivers.filter(
            driver__in=prv_drivers
        )
        prev_to_buy = current_racedrivers.exclude(
            driver__in=prv_drivers
        )

        self.fields["tactic"] = forms.ChoiceField(choices=TACTIC_CHOICES, initial=self.prev_race_team.tactic)
        self.fields["token"] = forms.IntegerField(disabled=True, required=False, initial=self.prev_race_team.token)
        self.fields["budget"] = forms.DecimalField(disabled=True, required=False, initial=self.prev_race_team.budget)
        self.fields["race_drivers"] = RaceDriverMultipleChoiceField(
            label="",
            queryset=current_racedrivers,
            required=False,
            widget=forms.SelectMultiple(attrs={'style': 'display: None'})
        )
        self.fields["to_sell"] = RaceDriverMultipleChoiceField(
            label="Satıyorum",
            required=False,
            queryset=self.old_race_drivers,
            widget=CheckboxSelectMultipleWithPrice()
        )
        self.fields["to_buy"] = RaceDriverMultipleChoiceField(
            label="Alıyorum",
            required=False,
            queryset=prev_to_buy,
            widget=CheckboxSelectMultipleWithPrice()
        )

    def clean(self):
        cleaned_data = super().clean()

        # Clean race drivers
        to_sell = cleaned_data.get("to_sell", RaceDriver.objects.none())
        to_buy = cleaned_data.get("to_buy", RaceDriver.objects.none())
        race_drivers = self.old_race_drivers.difference(to_sell).union(to_buy)
        if not race_drivers:
            raise forms.ValidationError("Takımınız en az bir sürücüden oluşmalıdır.")
        if len(race_drivers) > MAX_DRIVERS_IN_A_TEAM:
            raise forms.ValidationError("Takımınızda 8'den fazla sürücü olamaz.")
        cleaned_data["race_drivers"] = race_drivers

        # Clean token
        token = self.prev_race_team.token
        token -= to_sell.count() + to_buy.count()
        if token < 0:
            raise forms.ValidationError("Haklarınız bitti")
        cleaned_data['token'] = token
        self.instance.token = token

        # Clean budget
        left_budget = self.prev_race_team.budget
        deposit = sum(race_driver.price for race_driver in to_sell)
        withdraw = sum(race_driver.discounted_price() for race_driver in to_buy)
        left_budget += deposit - withdraw
        if left_budget < 0:
            raise forms.ValidationError("Bütçeniz eksi olamaz.")
        cleaned_data['budget'] = left_budget
        self.instance.budget = left_budget

        return cleaned_data
