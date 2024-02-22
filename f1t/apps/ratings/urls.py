from django.urls import include, path

from . import views

app_name = "ratings"
urlpatterns = [
    # Yarışı Puanla paths
    path('<str:series>/<int:year>/puanla/', views.SeasonRatingView.as_view(), name='season_ratings'),
    path('<str:series>/puanla/', views.SeriesRatingView.as_view(), name='series_ratings'),
]
