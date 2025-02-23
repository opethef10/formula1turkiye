from django.urls import path
from .views import PredictionFormView, PredictionDetailView, PredictionListView

app_name = 'season_predictions'
urlpatterns = [
    path('<str:series>/<int:year>/season_predictions/', PredictionListView.as_view(), name='prediction-list'),
    path('<str:series>/<int:year>/season_predictions/new/', PredictionFormView.as_view(), name='prediction-form'),
    path('<str:series>/<int:year>/season_predictions/<str:username>/', PredictionDetailView.as_view(), name='prediction-detail'),
]
