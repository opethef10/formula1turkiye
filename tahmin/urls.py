from django.urls import path

from . import views

app_name = "tahmin"
urlpatterns = [
    path('', views.ChampionshipListView.as_view(), name='home'),
    path('<slug:champ>/', views.ChampionshipDetailView.as_view(), name='championship_detail'),
    path('<slug:champ>/races/', views.RaceListView.as_view(), name='race_list'),
    path('<slug:champ>/races/<int:round>/', views.RaceDetailView.as_view(), name='race_detail'),
    path('<slug:champ>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<slug:champ>/teams/new/', views.NewTahminView.as_view(), name='new_team_form'),
]
