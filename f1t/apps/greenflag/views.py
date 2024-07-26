from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from f1t.apps.fantasy.models import Championship
from .models import GreenFlag


class GreenFlagListView(ListView):
    allow_empty = False
    template_name = "greenflag/greenflag_list.html"
    model = GreenFlag
    queryset = GreenFlag.objects.select_related('race', 'race__championship')


class GreenFlagDetailView(DetailView):
    template_name = "greenflag/greenflag_detail.html"
    model = GreenFlag
