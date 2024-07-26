from django.contrib import admin

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

class GreenflagAdmin(SelectRelatedModelAdmin):
    list_select_related = ["race", "race__championship"]
    related_fields = {
        'race': {
            'model': Race,
            'related_fields': ["championship"],
        },
    }

admin.site.register(GreenFlag, GreenflagAdmin)
