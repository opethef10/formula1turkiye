from django.urls import path

from . import views

app_name = "fantasy"
urlpatterns = [
    path('', views.ChampionshipListView.as_view(), name='home'),
    path('<slug:champ>/drivers/', views.DriverListView.as_view(), name='driver_list'),
    path('<slug:champ>/', views.RaceListView.as_view(), name='race_list'),
    path('<slug:champ>/<int:round>/', views.RaceDetailView.as_view(), name='race_detail'),
    path('<slug:champ>/<int:round>/edit/', views.RaceDriverUpdateView.as_view(), name='race_edit'),
    path('<slug:champ>/teams/', views.TeamListView.as_view(), name='team_list'),
    path('<slug:champ>/teams/new/', views.NewTeamView.as_view(), name='new_team_form'),
    path('<slug:champ>/teams/edit/', views.EditTeamView.as_view(), name='edit_team_form'),
    path('<slug:champ>/teams/<str:username>/', views.TeamDetailView.as_view(), name='team_detail'),
]
