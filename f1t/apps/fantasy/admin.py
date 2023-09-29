from django.apps import apps
from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django_summernote.admin import SummernoteModelAdmin

app_models = apps.get_app_config('fantasy').get_models()
for model in app_models:
    admin.site.register(model)


class FlatPageAdmin(SummernoteModelAdmin):
    pass


admin.site.unregister(FlatPage)
admin.site.register(FlatPage, FlatPageAdmin)

