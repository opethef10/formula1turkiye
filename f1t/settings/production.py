from pathlib import Path

from decouple import config, Csv

from ._base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', cast=Csv())

VAR_DIR = Path("/var/www/")

STATIC_ROOT = VAR_DIR / "static"
MEDIA_ROOT = VAR_DIR / "media"
LOG_PATH = VAR_DIR / "f1t.log"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
SERVER_EMAIL = config("DJANGO_SERVER_EMAIL")
EMAIL_HOST_USER = config("DJANGO_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("DJANGO_EMAIL_HOST_PASSWORD")

LOGGING['handlers']['file'] = {
    'level': 'INFO',
    'class': 'logging.FileHandler',
    'filename': LOG_PATH,
    'formatter': 'verbose',
}
LOGGING['loggers']['f1t']["handlers"] = ["file"]

