import os
import sys

path = '/home/formula1turkiye/formula1turkiye.pythonanywhere.com'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'f1t.settings.production'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

