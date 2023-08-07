from django.urls import path

from . import views

app_name = "tahmin"
urlpatterns = [
    path('', views.ChampionshipListView.as_view(), name='home'),
    path('<slug:champ>/', views.RaceListView.as_view(), name='race_list'),
    path('<slug:champ>/last/', views.LastRaceRedirectView.as_view(), name='redirect_last_race'),
    path('<slug:champ>/<int:round>/', views.RaceTahminView.as_view(), name='race_tahmins'),
    path('<slug:champ>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<slug:champ>/teams/new/', views.NewTahminView.as_view(), name='new_team_form'),
]
