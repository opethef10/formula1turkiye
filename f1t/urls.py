"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the 'include()' function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.conf import settings
from django.contrib.flatpages.views import flatpage
from django.views.generic import TemplateView

from .views import HomeView, ContactView
from .urlresolvers import solid_i18n_patterns

patterns = [
    path('admin/clearcache/', include('clearcache.urls')),
    path('admin/', admin.site.urls),
    path("accounts/", include("f1t.apps.accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("contact/", ContactView.as_view(), name='contact'),
    path("pages/", include("django.contrib.flatpages.urls")),
    path('__summernote/', include('django_summernote.urls')),
    path('', include('pwa.urls')),
    path('', HomeView.as_view(), name='home'),
    path("", include("f1t.apps.fantasy.urls")),
]

if settings.DEBUG:
    patterns.append(path('__debug__/', include('debug_toolbar.urls')))

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n"))
]
urlpatterns += solid_i18n_patterns(*patterns)
