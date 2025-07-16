from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.urls import path
from mdeditor.widgets import MDEditorWidget

from .models import *
from .views import CopyFantasyElementsView


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
            path("fantasycopy/", self.admin_site.admin_view(CopyFantasyElementsView.as_view()), name="copy_fantasy_elements"),
        ]
        return custom_urls + urls

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

