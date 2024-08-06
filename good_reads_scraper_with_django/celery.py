from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'good_reads_scraper_with_django.settings')

app = Celery('good_reads_scraper_with_django', broker=settings.CELERY_BROKER_URL)
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'scrape-new-items-every-3-seconds': {
        'task': 'goodread.tasks.good_reads_search_by_keyword_task',
        'schedule': 3.0,  # in seconds
    },
    'every-60-seconds-scrape-remain-book-search-items': {
        'task': 'goodread.tasks.good_reads_scrape_remain_book_search_item',
        'schedule': crontab(minute='*/1'),  # Runs every minute
    },
    'every-60-seconds-scrape-remain-group-search-items': {
        'task': 'goodread.tasks.good_reads_scrape_remain_group_search_item',
        'schedule': crontab(minute='*/1'),  # Runs every minute
    },

}

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
