"""
Celery configuration for ConstructOS.
"""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('constructos')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks([
    'backend.apps.core',
    'backend.apps.crm',
    'backend.apps.erp',
    'backend.apps.construction',
])

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
