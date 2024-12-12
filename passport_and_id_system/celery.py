import os
from django.conf import settings
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "passport_and_id_system.settings")

app = Celery('passport_and_id_system')
app.config_from_object(f'django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
