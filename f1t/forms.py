from django import forms
from django_recaptcha.fields import ReCaptchaField

class ContactForm(forms.Form):
    first_name = forms.CharField(max_length=50, label="Ad")
    last_name = forms.CharField(max_length=50, label="Soyad")
    email = forms.EmailField(label="E-posta")
    message = forms.CharField(widget=forms.Textarea, label="Mesaj")
    captcha = ReCaptchaField(label="Doğrulama")

