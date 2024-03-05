"""
WSGI config for rinha project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from rinha import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rinha.settings')

if settings.USE_STATIC_FILE_HANDLER_FROM_WSGI:
    application = StaticFilesHandler(get_wsgi_application())
else:
    application = get_wsgi_application()
