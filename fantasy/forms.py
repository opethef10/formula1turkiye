from django import forms
from .models import Circuit, Driver

class PostForm(forms.ModelForm):
    class Meta:
        model = Circuit
        fields = ['country', ]

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'What is on your mind?'}
        ),
        max_length=4000,
        help_text='The max length of the text is 4000.'
    )

    class Meta:
        model = Driver
        fields = ['forename', 'surname']
