from django.urls import path
from django.views.generic.base import TemplateView

from . import views

app_name = "fantasy"
urlpatterns = [
    path('', views.ChampionshipListView.as_view(), name='home'),
    path('<slug:champ>/', views.ChampionshipDetailView.as_view(), name='championship_detail'),
    path('<slug:champ>/drivers/', views.DriverListView.as_view(), name='driver_list'),
    path('<slug:champ>/races/', views.RaceListView.as_view(), name='race_list'),
    path('<slug:champ>/races/<int:round>/', views.RaceDetailView.as_view(), name='race_detail'),
    path('<slug:champ>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<slug:champ>/teams/new/', views.NewTeamView.as_view(), name='new_team_form'),
    path('<slug:champ>/teams/<int:pk>/', views.TeamDetailView.as_view(), name='team_detail'),
    path('drivers/<slug:driver_slug>/', views.DriverDetailView.as_view(), name='driver_detail'),
]
