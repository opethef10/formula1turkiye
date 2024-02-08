from django.urls import path

from . import views

app_name = "tahmin"
urlpatterns = [
    path('last/tahmin/', views.LastRaceRedirectView.as_view(), name='redirect_last_race'),
    path('<int:round>/tahmin/', views.RaceTahminView.as_view(), name='race_tahmins'),
    path('tahmin/', views.TeamListView.as_view(), name='team_list'),
    path('tahmin/new/', views.NewTahminView.as_view(), name='new_team_form'),
]
