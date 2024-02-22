from django.urls import include, path

from . import views

app_name = "formulapp"
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
    path('<str:series>/stats/drivers/wins/', views.StatsForDriverWinView.as_view(), name='stats_driver_wins'),
    path('<str:series>/stats/drivers/poles/', views.StatsForDriverPoleView.as_view(), name='stats_driver_poles'),

    # Season paths
    path('<str:series>/', views.SeasonsListView.as_view(), name='season_list'),
    path('<str:series>/<int:year>/drivers/', views.DriverStatsView.as_view(), name='driver_stats'),
    path('<str:series>/<int:year>/', views.RaceListView.as_view(), name='race_list'),
    path('<str:series>/<int:year>/last/', views.LastRaceRedirectView.as_view(), name='redirect_last_race'),
    path('<str:series>/<int:year>/<int:round>/', views.RaceDetailView.as_view(), name='race_detail'),

    # Tahmin ligi paths
    path('<str:series>/<int:year>/', include("f1t.apps.tahmin.urls")),
]
