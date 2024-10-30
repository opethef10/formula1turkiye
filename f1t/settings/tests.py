import logging

from ._base import *

SECRET_KEY = "INSECURE_DJANGO_SECRET_KEY_TO_BE_USED_AT_LOCAL_ENV"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

SILENCED_SYSTEM_CHECKS = ['django_recaptcha.recaptcha_test_key_error']

class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None


MIGRATION_MODULES = DisableMigrations()
logging.disable(logging.CRITICAL)
