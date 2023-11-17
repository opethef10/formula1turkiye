from django.urls import path

from . import views

app_name = "tahmin"
urlpatterns = [
    path('', views.ChampionshipListView.as_view(), name='home'),
    path('<str:series>/<int:year>/', views.RaceListView.as_view(), name='race_list'),
    path('<str:series>/<int:year>/last/', views.LastRaceRedirectView.as_view(), name='redirect_last_race'),
    path('<str:series>/<int:year>/<int:round>/', views.RaceTahminView.as_view(), name='race_tahmins'),
    path('<str:series>/<int:year>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<str:series>/<int:year>/teams/new/', views.NewTahminView.as_view(), name='new_team_form'),
]
