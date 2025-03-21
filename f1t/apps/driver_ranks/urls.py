from django.urls import path
from .views import DriverRankListView, DragDropRankView, DriverRanksDetailView, DriverPointsView

app_name = 'driver_ranks'
urlpatterns = [
    path('<str:series>/<int:year>/driver_ranks/', DriverRankListView.as_view(), name='driver-rank-list'),
    path('<str:series>/<int:year>/driver_ranks/new/', DragDropRankView.as_view(), name='driver-rank-form'),
    path('<str:series>/<int:year>/driver_ranks/points/', DriverPointsView.as_view(), name='driver_points'),
    path('<str:series>/<int:year>/driver_ranks/<str:username>/', DriverRanksDetailView.as_view(), name='driver-rank-detail'),
]
