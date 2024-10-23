from django.urls import include, path

from . import views

app_name = "formula"
urlpatterns = [
    # Formula paths
    path('circuits/', views.CircuitListView.as_view(), name='circuit_list'),
    path('circuits/<pk>/', views.CircuitDetailView.as_view(), name='circuit_detail'),

    path('drivers/', views.AllDriverListView.as_view(), name='all_driver_list'),
    path('drivers/<slug>/', views.DriverDetailView.as_view(), name='driver_detail'),
    path('drivers/<slug>/races/', views.DriverResultsView.as_view(), name='driver_results'),
    path('drivers/<slug>/wins/', views.DriverWinsView.as_view(), name='driver_wins'),
    path('drivers/<slug>/poles/', views.DriverPolesView.as_view(), name='driver_poles'),
    path('drivers/<slug>/flaps/', views.DriverFastestLapsView.as_view(), name='driver_flaps'),
    path('drivers/<slug>/hattricks/', views.DriverHatTricksView.as_view(), name='driver_hattricks'),
    path('drivers/<slug>/podiums/', views.DriverPodiumsView.as_view(), name='driver_podiums'),

    path('constructors/', views.ConstructorListView.as_view(), name='constructor_list'),
    path('constructors/<slug>/', views.ConstructorDetailView.as_view(), name='constructor_detail'),

    # Series Stats
    path('<str:series>/stats/', views.StatsForSeriesView.as_view(), name='stats_series'),
    path('<str:series>/stats/drivers/', views.StatsForDriverTemplateView.as_view(), name='stats_drivers'),
    path('<str:series>/stats/drivers/wins/', views.StatsForDriverWinView.as_view(), name='stats_driver_wins'),
    path('<str:series>/stats/drivers/poles/', views.StatsForDriverPoleView.as_view(), name='stats_driver_poles'),
    path('<str:series>/stats/drivers/podiums/', views.StatsForDriverPodiumView.as_view(), name='stats_driver_podiums'),
    path('<str:series>/stats/drivers/races/', views.StatsForDriverRaceView.as_view(), name='stats_driver_races'),
    path('<str:series>/stats/drivers/without_win/', views.StatsForDriverWithoutWinView.as_view(), name='stats_driver_without_win'),
    path('<str:series>/stats/drivers/finishes/', views.StatsForDriverFinishedView.as_view(), name='stats_driver_finishes'),

    # Season paths
    path('<str:series>/', views.SeasonsListView.as_view(), name='season_list'),
    path('<str:series>/<int:year>/stats/', views.SeasonStatsView.as_view(), name='season_stats'),
    path('<str:series>/<int:year>/stats/supergrid/', views.SeasonSupergridView.as_view(), name='season_supergrid'),
    path('<str:series>/<int:year>/', views.RaceListView.as_view(), name='race_list'),
    path('<str:series>/<int:year>/last/', views.LastRaceRedirectView.as_view(), name='redirect_last_race'),
    path('<str:series>/<int:year>/<int:round>/', views.RaceDetailView.as_view(), name='race_detail'),
    path('<str:series>/<int:year>/<int:round>/fantasy/', views.RaceFantasyView.as_view(), name='fantasy_race_results'),
    path('<str:series>/<int:year>/last/fantasy/', views.LastRaceFantasyRedirectView.as_view(), name='redirect_last_fantasy_result'),
    path('<str:series>/<int:year>/<int:round>/edit/', views.RaceDriverUpdateView.as_view(), name='race_edit'),

    # Fantasy paths
    path('<str:series>/<int:year>/teams/', views.FantasyStandingsView.as_view(), name='team_list_deprecated'),
    path('<str:series>/<int:year>/fantasy/', views.FantasyStandingsView.as_view(), name='team_list'),
    path('<str:series>/<int:year>/fantasy/stats/', views.DriverStatsView.as_view(), name='driver_stats'),
    path('<str:series>/<int:year>/teams/new/', views.NewTeamView.as_view(), name='new_team_form_deprecated'),
    path('<str:series>/<int:year>/fantasy/new/', views.NewTeamView.as_view(), name='new_team_form'),
    path('<str:series>/<int:year>/teams/edit/', views.EditTeamView.as_view(), name='edit_team_form_deprecated'),
    path('<str:series>/<int:year>/fantasy/edit/', views.EditTeamView.as_view(), name='edit_team_form'),
    path('<str:series>/<int:year>/teams/me/', views.FantasyProfileRedirectView.as_view(), name='redirect_my_team_deprecated'),
    path('<str:series>/<int:year>/fantasy/me/', views.FantasyProfileRedirectView.as_view(), name='redirect_my_team'),
    path('<str:series>/<int:year>/teams/<str:username>/', views.FantasyUserProfileView.as_view(), name='team_detail_deprecated'),
    path('<str:series>/<int:year>/fantasy/<str:username>/', views.FantasyUserProfileView.as_view(), name='team_detail'),

    # Tahmin ligi paths
    path('<str:series>/<int:year>/', include("f1t.apps.tahmin.urls")),
]
