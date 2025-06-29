import os

from django.core.wsgi import get_wsgi_application

# Django settings modulini korsatamiz (projektingiz nomiga qarab ozgartiring)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()