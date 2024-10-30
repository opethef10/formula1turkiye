from django import forms
from django_recaptcha.fields import ReCaptchaField


class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
    captcha = ReCaptchaField()
