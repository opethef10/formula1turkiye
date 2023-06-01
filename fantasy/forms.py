from django import forms
from django.forms import modelformset_factory

from .models import Driver, RaceTeam, RaceDriver, TACTIC_CHOICES


class RaceDriverMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, racedriver):
        return f"{racedriver.driver}: {racedriver.price}₺"


class DiscountedRaceDriverMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, racedriver):
        return f"{racedriver.driver}: {racedriver.discounted_price()}₺"


class CheckboxSelectMultipleWithPrice(forms.CheckboxSelectMultiple):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        option['attrs']['price'] = value.instance.price
        option['attrs']['discounted_price'] = value.instance.discounted_price()
        return option


class NewTeamForm(forms.ModelForm):

    class Meta:
        model = RaceTeam
        fields = ["tactic", "token", "budget", "race_drivers"]

    def __init__(self, request, current_race, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.starting_budget = current_race.championship.starting_budget
        self.beginning_token = current_race.championship.beginning_token
        self.max_drivers_in_a_team = current_race.championship.max_drivers_in_team
        self.fields['tactic'].label = "Taktik"
        self.fields["budget"] = forms.DecimalField(label="Kalan Bütçe", disabled=True, required=False)
        self.fields["token"] = forms.IntegerField(label="Kalan Hak", disabled=True, required=False, initial=self.beginning_token)
        self.fields["race_drivers"] = RaceDriverMultipleChoiceField(
            label="Sürücüler",
            queryset=RaceDriver.objects.select_related("driver").filter(
                race=current_race
            ),
            widget=CheckboxSelectMultipleWithPrice(),
            help_text="En fazla 8 pilot seçebilirsiniz."
        )

    def clean(self):
        cleaned_data = super().clean()
        race_drivers = self.cleaned_data.get('race_drivers', RaceDriver.objects.none())
        cleaned_data["tactic"] = self.cleaned_data.get('tactic', "")
        cleaned_data['token'] = self.beginning_token
        cleaned_data['budget'] = self.starting_budget
        if len(race_drivers) == 0:
            self.add_error(None, "Takımınız en az bir sürücüden oluşmalıdır.")
        if len(race_drivers) > self.max_drivers_in_a_team:
            self.add_error(None, f"Takımınızda en fazla {self.max_drivers_in_a_team} sürücü olabilir.")

        total_price = sum(race_driver.price for race_driver in race_drivers)
        left_budget = self.starting_budget - total_price
        if left_budget < 0:
            self.add_error("budget", "Bütçeniz eksi olamaz.")
        cleaned_data['budget'] = left_budget
        return cleaned_data


class EditTeamForm(forms.ModelForm):

    class Meta:
        model = RaceTeam
        fields = ["race_drivers"]

    def __init__(self, request, current_race, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_drivers_in_a_team = current_race.championship.max_drivers_in_team
        prev_race = current_race.get_previous_by_datetime(championship=current_race.championship)
        current_racedrivers = current_race.driver_instances.select_related("driver")
        self.prev_race_team = prev_race.team_instances.get(team__user=request.user)
        prv_driver_ids = self.prev_race_team.race_drivers.values_list("driver", flat=True)
        self.old_race_drivers = current_racedrivers.filter(
            driver__in=prv_driver_ids
        ).order_by("-price")
        prev_to_buy = current_racedrivers.exclude(
            driver__in=prv_driver_ids
        )

        self.fields["tactic"] = forms.ChoiceField(label="Taktik", choices=TACTIC_CHOICES, initial=self.prev_race_team.tactic)
        self.fields["token"] = forms.IntegerField(label="Kalan Hak", disabled=True, required=False, initial=self.prev_race_team.token)
        self.fields["budget"] = forms.DecimalField(label="Kalan Bütçe", disabled=True, required=False, initial=self.prev_race_team.budget)
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
        self.fields["to_buy"] = DiscountedRaceDriverMultipleChoiceField(
            label="Alıyorum",
            required=False,
            queryset=prev_to_buy,
            widget=CheckboxSelectMultipleWithPrice()
        )

    def clean(self):
        cleaned_data = super().clean()
        self.instance.tactic = cleaned_data['tactic']

        # Clean race drivers
        to_sell = cleaned_data.get("to_sell", RaceDriver.objects.none())
        to_buy = cleaned_data.get("to_buy", RaceDriver.objects.none())
        race_drivers = self.old_race_drivers.exclude(id__in=to_sell) | to_buy
        if not race_drivers:
            self.add_error(None, "Takımınız en az bir sürücüden oluşmalıdır.")
        if len(race_drivers) > self.max_drivers_in_a_team:
            self.add_error(None, f"Takımınızda en fazla {self.max_drivers_in_a_team} sürücü olabilir.")
        cleaned_data["race_drivers"] = race_drivers

        # Clean token
        token = self.prev_race_team.token
        token -= to_sell.count() + to_buy.count()
        if token < 0:
            self.add_error("token", "Haklarınız eksi olamaz.")
        cleaned_data['token'] = token
        self.instance.token = token

        # Clean budget
        left_budget = self.prev_race_team.budget
        deposit = sum(race_driver.price for race_driver in to_sell)
        withdraw = sum(race_driver.discounted_price() for race_driver in to_buy)
        left_budget += deposit - withdraw
        if left_budget < 0:
            self.add_error("budget", "Bütçeniz eksi olamaz.")
        cleaned_data['budget'] = left_budget
        self.instance.budget = left_budget

        return cleaned_data


class RaceDriverEditForm(forms.ModelForm):
    class Meta:
        model = RaceDriver
        fields = ["driver", "discount", "price", "qualy", "grid_sprint", "sprint", "grid", "result", "fastest_lap", "sprint_fastest_lap"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


RaceDriverFormSet = modelformset_factory(
    RaceDriver,
    fields=["driver", "discount", "price", "qualy", "grid_sprint", "sprint", "grid", "result", "fastest_lap", "sprint_fastest_lap"],
    extra=0
)
