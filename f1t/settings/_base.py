"""
Django settings for project Formula 1 Türkiye.

Generated by 'django-admin startproject' using Django 3.2.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path

from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _

PROJECT_DIR = Path(__file__).parent.parent
BASE_DIR = PROJECT_DIR.parent
ROOT_URLCONF = 'f1t.urls'
INTERNAL_IPS = ["127.0.0.1"]
DEBUG = False

INSTALLED_APPS = [
    'django.contrib.flatpages',
    'f1t.apps.accounts',
    'f1t.apps.fantasy',
    'f1t.apps.tahmin',
    'f1t.apps.ratings',
    'f1t.apps.greenflag',
    "django_minify_html",
    "django_extensions",
    "django_countries",
    # 'clearcache',
    'colorfield',
    'django_summernote',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    "django.contrib.redirects",
    'widget_tweaks',
    "pwa",
    "mobiledetect",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    "django_minify_html.middleware.MinifyHtmlMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [PROJECT_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
        },
    },
]


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# LOGGING
LOGGING = {
    'version': 1,
    # The version number of our log
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': "[%(asctime)s] (%(levelname)s) %(message)s",
            'datefmt': "%Y/%m/%d %H:%M:%S %z"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            'formatter': 'simple',
        },
    },
    'loggers': {
        'f1t': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "tr"
TIME_ZONE = "Europe/Istanbul"
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = (
    ('tr', _('Turkish')),
    # ('en', _('English')),
)
LOCALE_PATHS = [
    PROJECT_DIR / 'locale/',
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [PROJECT_DIR / 'static']
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

ADMINS = [
    ('Onur Arıkan', 'altimuray@gmail.com'),
    ('Semih Boz', 'semih.boz0@gmail.com'),
    ("Formula 1 Türkiye", "formula1turkiyef1t@gmail.com"),
]

EMAIL_SUBJECT_PREFIX = "[Formula 1 Türkiye] "

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# ==============================================================================
# FIRST-PARTY SETTINGS
# ==============================================================================
SITE_ID = 1

SECONDS = 1
MINUTES = 60 * SECONDS
HOURS = 60 * MINUTES

MAX_DRIVER_POSITION = 34
MAX_RACES_IN_SEASON = 24

# ==============================================================================
# THIRD-PARTY SETTINGS
# ==============================================================================

SUMMERNOTE_THEME = 'bs4'  # Show summernote with Bootstrap4

# ==============================================================================
# DJANGO COUNTRIES TEMPORARY SETTINGS
# ==============================================================================
from django_countries.widgets import LazyChoicesMixin

LazyChoicesMixin.get_choices = lambda self: self._choices
LazyChoicesMixin.choices = property(LazyChoicesMixin.get_choices, LazyChoicesMixin.set_choices)

# ==============================================================================
# PWA SETTINGS
# ==============================================================================
PWA_APP_NAME = 'Formula 1 Türkiye'
PWA_APP_DESCRIPTION = "Formula 1 Türkiye grubu ana sayfasına hoş geldiniz. Bu site, 4600'ü aşkın üyesiyle, " \
    "aktifleştiği 2015 yılından bu yana Türkiye'nin en büyük Formula 1 Facebook grubu olan Formula 1 Türkiye'nin " \
    "düzenlediği Fantasy ve Tahmin Ligleri için kurduğumuz web sitesidir. Dilerseniz Quiz Night, Yarışı Puanla ve " \
    "Elo Sıralama Projesi gibi diğer ürünlerimize de bakabilirsiniz."
PWA_APP_THEME_COLOR = '#0A0302'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_SCOPE = '/'
PWA_APP_ORIENTATION = 'any'
PWA_APP_START_URL = '/'
PWA_APP_STATUS_BAR_COLOR = 'default'
PWA_APP_ICONS = [
    {
        'src': '/static/icons/android-chrome-192x192.png',
        'sizes': '160x160'
    }
]
PWA_APP_ICONS_APPLE = [
    {
        'src': '/static/icons/apple-touch-icon.png',
        'sizes': '160x160'
    }
]
PWA_APP_SPLASH_SCREEN = [
    {
        'src': '/static/icons/apple-touch-icon.png',
        'media': '(device-width: 320px) and (device-height: 568px) and (-webkit-device-pixel-ratio: 2)'
    }
]
PWA_APP_DIR = 'ltr'
PWA_APP_LANG = 'tr'
PWA_SERVICE_WORKER_PATH = PROJECT_DIR / 'static' / 'js' / 'serviceworker.js'
