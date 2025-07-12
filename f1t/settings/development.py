import mimetypes

from django.core.management.commands.runserver import Command as runserver

from ._base import *

runserver.default_port = "8888"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "INSECURE_DJANGO_SECRET_KEY_TO_BE_USED_AT_LOCAL_ENV"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", f"{PROJECT_SLUG}.local"]
CSRF_TRUSTED_ORIGINS = [f"https://{PROJECT_SLUG}.local"]

# For Docker
# `debug` is only True in templates if the vistor IP is in INTERNAL_IPS.
INTERNAL_IPS = type(str("c"), (), {"__contains__": lambda *a: True, "copy": lambda self: self})()

SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS.extend(
    [
        "debug_toolbar",
        "fontawesomefree"
    ]
)

MIDDLEWARE.insert(5, "debug_toolbar.middleware.DebugToolbarMiddleware")
MIDDLEWARE.append('mobiledetect.middleware.DetectMiddleware')

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

mimetypes.add_type("application/javascript", ".js", True)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    # 'SHOW_TOOLBAR_CALLBACK': lambda _request: DEBUG
}

