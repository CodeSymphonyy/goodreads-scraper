from celery import shared_task
from django.db import transaction, OperationalError
from time import sleep
from .models import SearchByKeyword, BookSearchByKeywordItem, GroupSearchByKeywordItem, TaskStatus
from .scraper_handler import ScraperHandler
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)


def acquire_lock(task_name, retries=5, delay=2):
    while retries > 0:
        try:
            with transaction.atomic():
                task_status, created = TaskStatus.objects.select_for_update().get_or_create(task_name=task_name)
                if task_status.status == 'in_progress':
                    logger.info(f'Task {task_name} is already in progress. Retrying...')
                    retries -= 1
                    time.sleep(delay)  # Delay before retrying
                else:
                    task_status.status = 'in_progress'
                    task_status.save()
                    return task_status
        except OperationalError as e:
            if 'database is locked' in str(e):
                retries -= 1
                logger.warning(f'Database is locked. Retrying in {delay} second(s)... ({retries} retries left)')
                time.sleep(delay)
            else:
                raise e
    # If retries are exhausted, log and skip the task
    logger.warning(f'Unable to acquire lock for task {task_name}. Skipping execution.')
    return None


def release_lock(task_status):
    if task_status:  # Ensure task_status is not None
        task_status.status = 'completed'
        task_status.save()


@shared_task(bind=True)
def good_reads_search_by_keyword_task(self):
    task_name = 'good_reads_search_by_keyword_task'
    task_status = acquire_lock(task_name)

    if task_status is None:
        # Skip execution if lock wasn't acquired
        return {'status': 'skipped', 'reason': 'Unable to acquire lock'}

    try:
        # Task logic here
        unsaved_searches = SearchByKeyword.objects.filter(is_active=True).exclude(
            book_search_by_keyword_items__is_scraped=False)

        for search in unsaved_searches:
            try:
                # Update the status to 'In Progress'
                search.status = 'In Progress'
                search.save()

                logger.info(f'Processing search: {search.keyword}')
                scraper_handler = ScraperHandler(
                    base_url=settings.GOOD_READS_BASE_URL,
                    search_url=settings.GOOD_READS_SEARCH_URL
                )
                scraper_handler.search_by_keyword(search_by_keyword_instance=search)

                # Update the status to 'Completed' after successful scraping
                search.status = 'Completed'
                search.processed = True  # Mark as processed
                search.save()

                logger.info(f'Successfully processed search: {search.keyword}')

            except Exception as e:
                # Update the status to 'Failed' if an exception occurs
                search.status = 'Failed'
                search.save()

                logger.error(f'Error processing search: {search.keyword}, Error: {e}')
                continue  # Continue processing the next search

        logger.info(f'Task {task_name} completed successfully.')

    except OperationalError as e:
        logger.error(f'Error in task {task_name}: {e}')
        raise e

    finally:
        release_lock(task_status)  # Release the lock only if it's acquired

    return {'status': 'finished'}


@shared_task(bind=True)
def good_reads_scrape_remain_book_search_item(self):
    task_name = 'good_reads_scrape_remain_book_search_item'
    task_status = acquire_lock(task_name)

    if task_status is None:
        # Skip execution if lock wasn't acquired
        return {'status': 'skipped', 'reason': 'Unable to acquire lock'}

    try:
        # Task logic here
        remain_book_search_items = BookSearchByKeywordItem.objects.filter(is_scraped=False)
        logger.info(f'Found {remain_book_search_items.count()} unscraped book items')

        scraper_handler = ScraperHandler(
            base_url=settings.GOOD_READS_BASE_URL,
            search_url=settings.GOOD_READS_SEARCH_URL
        )

        for remain_book_search_item in remain_book_search_items:
            logger.debug(f'Processing book item: {remain_book_search_item.title}')
            book, genres = scraper_handler.parse_book_detail(url=remain_book_search_item.url)
            remain_book_search_item.book = book
            remain_book_search_item.is_scraped = True
            remain_book_search_item.save()

        logger.info(f'Task {task_name} completed successfully.')

    except Exception as e:
        logger.error(f'Error in task {task_name}: {e}')
        raise e

    finally:
        release_lock(task_status)  # Release the lock only if it's acquired

    return {'status': 'finished'}


@shared_task(bind=True)
def good_reads_scrape_remain_group_search_item(self):
    task_name = 'good_reads_scrape_remain_group_search_item'
    task_status = acquire_lock(task_name)

    if task_status is None:
        # Skip execution if lock wasn't acquired
        return {'status': 'skipped', 'reason': 'Unable to acquire lock'}

    try:
        # Task logic here
        remain_group_search_items = GroupSearchByKeywordItem.objects.filter(is_scraped=False)
        logger.info(f'Found {remain_group_search_items.count()} unscraped group items')

        scraper_handler = ScraperHandler(
            base_url=settings.GOOD_READS_BASE_URL,
            search_url=settings.GOOD_READS_SEARCH_URL
        )

        for remain_group_search_item in remain_group_search_items:
            logger.debug(f'Processing group item: {remain_group_search_item.title}')
            group = scraper_handler.parse_group_detail(url=remain_group_search_item.url)
            remain_group_search_item.group = group
            remain_group_search_item.is_scraped = True
            remain_group_search_item.save()

        logger.info(f'Task {task_name} completed successfully.')

    except Exception as e:
        logger.error(f'Error in task {task_name}: {e}')
        raise e

    finally:
        release_lock(task_status)  # Release the lock only if it's acquired

    return {'status': 'finished'}
