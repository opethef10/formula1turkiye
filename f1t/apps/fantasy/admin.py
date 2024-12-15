from django.contrib import admin, messages
from django.contrib.flatpages.models import FlatPage
from django_summernote.admin import SummernoteModelAdmin
from django.shortcuts import render, redirect
from django.urls import path
from mdeditor.widgets import MDEditorWidget

from .forms import CopyFantasyElementsForm
from .management.commands.fantasycopy import Command
from .models import *

class SelectRelatedModelAdmin(admin.ModelAdmin):
    related_fields = {}
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if 'queryset' in kwargs:
            kwargs['queryset'] = kwargs['queryset'].select_related()
        else:
            db = kwargs.pop('using', None)
            kwargs['queryset'] = db_field.remote_field.model._default_manager.using(db).complex_filter(db_field.remote_field.limit_choices_to).select_related()
        if db_field.name in self.related_fields:
            related_info = self.related_fields[db_field.name]
            model = related_info['model']
            related_fields = related_info['related_fields']
            queryset = model.objects.all()
            if self.related_fields[db_field.name].get('query_length'):
                queryset = queryset[:self.related_fields[db_field.name]['query_length']]
            for related_field in related_fields:
                queryset = queryset.select_related(related_field)
            kwargs['queryset'] = queryset
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ChampionshipConstructorAdmin(SelectRelatedModelAdmin):
    list_select_related = ["championship", "constructor"]

admin.site.register(ChampionshipConstructor, ChampionshipConstructorAdmin)

class ChampionshipAdmin(admin.ModelAdmin):
    change_list_template = "admin/championship_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("fantasycopy/", self.admin_site.admin_view(self.copy_fantasy_elements_view), name="copy_fantasy_elements"),
        ]
        return custom_urls + urls

    def copy_fantasy_elements_view(self, request):
        if request.method == "POST":
            form = CopyFantasyElementsForm(request.POST)
            if form.is_valid():
                series = form.cleaned_data["series"]
                budget = form.cleaned_data["budget"]
                token = form.cleaned_data["token"]

                try:
                    # Invoke the command logic
                    command = Command()
                    command.handle(series=series, budget=budget, token=token)
                    messages.success(request, "Fantasy elements copied successfully.")
                    return redirect("..")
                except Exception as e:
                    messages.error(request, f"Error: {e}")
        else:
            form = CopyFantasyElementsForm()

        return render(request, "admin/copy_fantasy_elements_form.html", {"form": form})



class CircuitAdmin(SelectRelatedModelAdmin):
    pass

class ConstructorAdmin(SelectRelatedModelAdmin):
    pass

class DriverAdmin(SelectRelatedModelAdmin):
    pass

class RaceAdmin(SelectRelatedModelAdmin):
    list_select_related = ["championship"]

class RaceDriverAdmin(SelectRelatedModelAdmin):
    list_select_related = ["race", "driver", "race__championship"]
    related_fields = {
        'race': {
            'model': Race,
            'related_fields': ['championship'],
        },
    }

class RaceTeamAdmin(SelectRelatedModelAdmin):
    list_select_related = ["race", "user", "race__championship"]
    related_fields = {
        'race': {
            'model': Race,
            'related_fields': ['championship'],
        },
    }

class RaceTeamDriverAdmin(SelectRelatedModelAdmin):
    list_select_related = ["raceteam__race", "racedriver__driver", "racedriver__race", "racedriver__race", "racedriver__race__championship", "raceteam__race__championship", "raceteam__user"]
    related_fields = {
        'raceteam': {
            'model': RaceTeam,
            'related_fields': ["race", "user", "race__championship"],
        },
        'racedriver': {
            'model': RaceDriver,
            'related_fields': ["race", "driver", "race__championship"],
        },
    }

admin.site.register(Championship, ChampionshipAdmin)
admin.site.register(Circuit, CircuitAdmin)
admin.site.register(Constructor, ConstructorAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Race, RaceAdmin)
admin.site.register(RaceDriver, RaceDriverAdmin)
admin.site.register(RaceTeam, RaceTeamAdmin)
admin.site.register(RaceTeamDriver, RaceTeamDriverAdmin)

class MDEditorAdmin (admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }


class FlatPageAdmin(MDEditorAdmin):
    pass


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

