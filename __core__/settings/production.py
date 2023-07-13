from pathlib import Path
from .base import *

from decouple import config, Csv

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = config('DJANGO_ALLOWED_HOSTS', cast=Csv())

VAR_DIR = Path("/var/www/formula1turkiye.pythonanywhere.com/")

STATIC_ROOT = VAR_DIR / "static"
MEDIA_ROOT = VAR_DIR / "media"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
SERVER_EMAIL = config("DJANGO_SERVER_EMAIL")
EMAIL_HOST_USER = config("DJANGO_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("DJANGO_EMAIL_HOST_PASSWORD")
