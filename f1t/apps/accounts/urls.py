from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.UserUpdateView.as_view(), name='profile'),
]
