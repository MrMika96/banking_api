import os
from datetime import datetime

from celery import Celery

# Set the default Django settings module for the 'celery' program.
from celery.schedules import crontab
from django.apps import apps

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'practice_2.settings')

app = Celery('practice_2', broker='redis://localhost')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'change_expiration_status_for_card': {
        'task': 'credit_cards.tasks.change_expiration_status_for_card',
        'schedule': crontab(hour=0, minute=0),
    },
    'update_currency_rates': {
        'task': 'banks.tasks.update_currency_rates',
        'schedule': crontab(hour=15, minute=0)
    }
}


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
