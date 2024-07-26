from django.urls import include, path

from . import views

app_name = "greenflag"
urlpatterns = [
    path('', views.GreenFlagListView.as_view(), name='greenflag_list'),
    path('<int:pk>/', views.GreenFlagDetailView.as_view(), name='greenflag_detail'),
]
