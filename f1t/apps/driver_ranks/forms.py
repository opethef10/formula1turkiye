from django import forms

from f1t.apps.fantasy.models import Driver


class DragDropRankForm(forms.Form):
    ranked_drivers = forms.CharField(widget=forms.HiddenInput())

    def clean_ranked_drivers(self):
        data = self.cleaned_data['ranked_drivers']
        try:
            driver_ids = [int(id) for id in data.split(',')]
        except:
            raise forms.ValidationError("Invalid format")

        # Verify all drivers are present and valid
        valid_drivers = set(Driver.objects.filter(
            pk__in=driver_ids
        ).values_list('id', flat=True))

        if len(driver_ids) != 20 or len(set(driver_ids)) != 20:
            raise forms.ValidationError("Invalid driver selection")

        return driver_ids
