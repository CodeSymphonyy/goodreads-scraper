from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SearchByKeyword
from .tasks import good_reads_search_by_keyword_task
from django.db import transaction
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=SearchByKeyword)
def trigger_scrape_on_save(sender, instance, created, **kwargs):
    if created:
        logger.info(f"post_save signal received for SearchByKeyword: {instance.keyword}, created: {created}")
        print(f"Signal received for SearchByKeyword: {instance.keyword}, created: {created}")
        # Check if a similar search already exists
        existing_search = SearchByKeyword.objects.filter(
            keyword=instance.keyword,
            search_type=instance.search_type,
            page_count=instance.page_count
        ).exists()

        if not existing_search:
            logger.info(f"Triggering Celery task for keyword: {instance.keyword}")
            print(f"Signal received for SearchByKeyword: {instance.keyword}, created: {created}")
            print(f"Triggering Celery task for keyword: {instance.keyword}")

            transaction.on_commit(lambda: good_reads_search_by_keyword_task.delay(
                keyword=instance.keyword.title,
                search_type=instance.search_type,
                page_count=instance.page_count
            ))
