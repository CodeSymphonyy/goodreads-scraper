from django.apps import AppConfig
from django.db.models.signals import post_save
import logging


class GoodreadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'goodread'

    def ready(self):
        from .models import SearchByKeyword
        import goodread.signals
        post_save.connect(goodread.signals.trigger_scrape_on_save, sender=SearchByKeyword)
        logging.basicConfig(level=logging.INFO)
