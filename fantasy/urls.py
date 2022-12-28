from django.urls import path
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='fantasy/home.html'), name='home'),
    path('championships/', views.ChampionshipListView.as_view(), name='championship_list'),
    path('championships/<slug>/', views.ChampionshipDetailView.as_view(), name='championship_detail'),
    path('championships/<slug>/drivers/', views.ChampionshipDriverListView.as_view(), name='season_driver_list'),
    path('championships/<slug>/races/', views.RaceListView.as_view(), name='race_list'),
    path('championships/<slug>/races/<int:round>/', views.RaceDetailView.as_view(), name='race_detail'),
    path('drivers/', views.DriverListView.as_view(), name='driver_list'),
    path('drivers/<slug>/', views.DriverDetailView.as_view(), name='driver_detail'),
]
