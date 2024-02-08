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
    path('constructors/', views.ConstructorListView.as_view(), name='constructor_list'),
    path('constructors/<slug>/', views.ConstructorDetailView.as_view(), name='constructor_detail'),

    # Season paths
    path('<str:series>/', views.SeasonsListView.as_view(), name='season_list'),
    path('<str:series>/<int:year>/drivers/', views.DriverStatsView.as_view(), name='driver_stats'),
    path('<str:series>/<int:year>/', views.RaceListView.as_view(), name='race_list'),
    path('<str:series>/<int:year>/last/', views.LastRaceRedirectView.as_view(), name='redirect_last_race'),
    path('<str:series>/<int:year>/<int:round>/', views.RaceDetailView.as_view(), name='race_detail'),
    path('<str:series>/<int:year>/<int:round>/edit/', views.RaceDriverUpdateView.as_view(), name='race_edit'),

    # Fantasy paths
    path('<str:series>/<int:year>/teams/', views.FantasyStandingsView.as_view(), name='team_list'),
    path('<str:series>/<int:year>/teams/new/', views.NewTeamView.as_view(), name='new_team_form'),
    path('<str:series>/<int:year>/teams/edit/', views.EditTeamView.as_view(), name='edit_team_form'),
    path('<str:series>/<int:year>/teams/<str:username>/', views.FantasyUserProfileView.as_view(), name='team_detail'),

    # Tahmin ligi paths
    path('<str:series>/<int:year>/', include("f1t.apps.tahmin.urls")),
]
