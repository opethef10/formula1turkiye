from math import sqrt, ceil, floor

from django import forms

from f1t.apps.fantasy.models import Race
from .models import Rating

SIGMA = 2
MIN_SCORE = 1
MAX_SCORE = 10
ROUND_DIGITS = 2

class RatingForm(forms.ModelForm):
    vote_count_1 = forms.IntegerField(label='1', required=True, initial=0, min_value=0)
    vote_count_2 = forms.IntegerField(label='2', required=True, initial=0, min_value=0)
    vote_count_3 = forms.IntegerField(label='3', required=True, initial=0, min_value=0)
    vote_count_4 = forms.IntegerField(label='4', required=True, initial=0, min_value=0)
    vote_count_5 = forms.IntegerField(label='5', required=True, initial=0, min_value=0)
    vote_count_6 = forms.IntegerField(label='6', required=True, initial=0, min_value=0)
    vote_count_7 = forms.IntegerField(label='7', required=True, initial=0, min_value=0)
    vote_count_8 = forms.IntegerField(label='8', required=True, initial=0, min_value=0)
    vote_count_9 = forms.IntegerField(label='9', required=True, initial=0, min_value=0)
    vote_count_10 = forms.IntegerField(label='10', required=True, initial=0, min_value=0)

    class Meta:
        model = Rating
        fields = ['vote_count_1', 'vote_count_2', 'vote_count_3', 'vote_count_4', 'vote_count_5', 'vote_count_6', 'vote_count_7', 'vote_count_8', 'vote_count_9', 'vote_count_10', 'onur', 'semih']

    def clean(self):
        cleaned_data = super().clean()
        vote_counts = [cleaned_data.get(f'vote_count_{score}', 0) for score in range(MIN_SCORE, MAX_SCORE + 1)]
        total_votes = sum(vote_counts)

        if total_votes <= 0:
            raise forms.ValidationError("En az 1 oy girilmesi gerekir.")

        mean = sum(score * count for score, count in enumerate(vote_counts, start=MIN_SCORE)) / total_votes
        sum_of_squares = sum(((score - mean) ** 2) * count for score, count in enumerate(vote_counts, start=MIN_SCORE))
        variance = sum_of_squares / total_votes
        standard_deviation = sqrt(variance)
        
        lower_threshold = max(MIN_SCORE, ceil(mean - SIGMA * standard_deviation))
        upper_threshold = min(MAX_SCORE, floor(mean + SIGMA * standard_deviation))
        
        accepted_vote_counts = vote_counts[lower_threshold - 1 : upper_threshold]
        accepted_total_votes = sum(accepted_vote_counts)
        race_score = sum(score * count for score, count in enumerate(accepted_vote_counts, start=lower_threshold)) / accepted_total_votes
        
        cleaned_data['score'] = round(race_score, ROUND_DIGITS)
        cleaned_data['amount'] = total_votes  # Add amount to cleaned data
        return cleaned_data

