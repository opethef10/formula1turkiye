from math import sqrt, ceil, floor

from django import forms

from .models import Rating


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = [
            *(f'vote_count_{score}' for score in range(Rating.MIN_SCORE, Rating.MAX_SCORE + 1)),
            'onur',
            'semih',
        ]

    def clean(self):
        cleaned_data = super().clean()
        vote_counts = [
            cleaned_data.get(f'vote_count_{score}', 0)
            for score in range(Rating.MIN_SCORE, Rating.MAX_SCORE + 1)
        ]
        total_votes = sum(vote_counts)

        if total_votes <= 0:
            raise forms.ValidationError("En az 1 oy girilmesi gerekir.")

        mean = sum(
            score * count
            for score, count
            in enumerate(vote_counts, start=Rating.MIN_SCORE)
        ) / total_votes
        sum_of_squares = sum(
            ((score - mean) ** 2) * count
            for score, count
            in enumerate(vote_counts, start=Rating.MIN_SCORE)
        )
        variance = sum_of_squares / total_votes
        standard_deviation = sqrt(variance)

        lower_threshold = max(Rating.MIN_SCORE, ceil(mean - Rating.SIGMA * standard_deviation))
        upper_threshold = min(Rating.MAX_SCORE, floor(mean + Rating.SIGMA * standard_deviation))

        accepted_vote_counts = vote_counts[lower_threshold - 1 : upper_threshold]
        accepted_total_votes = sum(accepted_vote_counts)
        race_score = sum(
            score * count
            for score, count
            in enumerate(accepted_vote_counts, start=lower_threshold)
        ) / accepted_total_votes

        cleaned_data['score'] = round(race_score, Rating.ROUND_DIGITS)
        cleaned_data['amount'] = total_votes
        return cleaned_data
