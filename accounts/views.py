from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import RedirectURLMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView

from .forms import SignUpForm


class UserUpdateView(SuccessMessageMixin, LoginRequiredMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('profile')
    success_message = "Profiliniz başarıyla güncellendi!"

    def get_object(self):
        return self.request.user


class SignUpView(SuccessMessageMixin, RedirectURLMixin, CreateView):
    """
    Allows the User to Create a New Account
    """
    form_class = SignUpForm
    template_name = "signup.html"
    next_page = reverse_lazy('home')
    success_message = "Üyeliğiniz başarıyla oluşturuldu!"

    def form_valid(self, form):
        valid = super().form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid
