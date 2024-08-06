import logging
import requests
import time
import random
from bs4 import BeautifulSoup
from django.conf import settings
from .models import Author, Genre, Book, BookGenre, Group, Keyword, SearchByKeyword, BookSearchByKeywordItem, \
    GroupSearchByKeywordItem

logger = logging.getLogger(__name__)


class ScraperHandler:
    def __init__(self, base_url, search_url):
        self.base_url = base_url
        self.search_url = search_url

    def request_to_target_url(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/58.0.3029.110 Safari/537.3'}
        logger.info(f'Fetching URL: {url}')

        # Random delay before making the request
        time.sleep(random.uniform(2, 5))  # Delay between 2 to 5 seconds

        return requests.get(url, headers=headers)

    def search_by_keyword(self, search_by_keyword_instance):
        search_items = list()
        logger.info(f'Starting search for keyword: {search_by_keyword_instance.keyword.title}')

        for i in range(1, search_by_keyword_instance.page_count + 1):
            try:
                url = self.search_url.format(
                    query=search_by_keyword_instance.keyword.title,
                    page=i,
                    search_type=search_by_keyword_instance.search_type,
                    tab=search_by_keyword_instance.search_type
                )
                logger.debug(f"Requesting URL: {url}")
                response = self.request_to_target_url(url)

                if response.status_code == 200:
                    logger.debug(
                        f"Successfully fetched page {i} for keyword {search_by_keyword_instance.keyword.title}")
                    soup = BeautifulSoup(response.text, 'html.parser')
                    new_items = self.extract_search_items(search_by_keyword=search_by_keyword_instance, soup=soup)
                    search_items += filter(None, new_items)  # Add only new items (no duplicates)
                    logger.info(f'Page {i}: Found {len(new_items)} items')
                else:
                    logger.error(f'Failed to fetch page {i}: Status code {response.status_code}')

            except Exception as e:
                logger.error(f"Error processing page {i} for keyword {search_by_keyword_instance.keyword.title}: {e}")

        if search_by_keyword_instance.search_type == 'books':
            for i, search_item in enumerate(search_items, 1):
                book, genres = self.parse_book_detail(url=search_item.url)
                search_item.book = book
                search_item.is_scraped = False
                search_item.save()
                data = {
                    'title': book.title,
                    'author': book.author.fullname,
                    'description': book.description,
                    'thumbnail': book.thumbnail,
                    'genres': genres,
                }
                logger.info(f'Book {i}: {data}')
        elif search_by_keyword_instance.search_type == 'groups':
            for i, search_item in enumerate(search_items, 1):
                group = self.parse_group_detail(url=search_item.url)
                search_item.group = group
                search_item.is_scraped = False
                search_item.save()
                data = {
                    'title': group.title,
                    'thumbnail': group.thumbnail,
                }
                logger.info(f'Group {i}: {data}')
        return len(search_items)

    def extract_search_items(self, search_by_keyword, soup):
        search_items = list()

        search_result_item = soup.findAll(
            'a',
            attrs={'class': settings.GOOD_READS_ITEM_CLASS[search_by_keyword.search_type]}
        )

        for a in search_result_item:
            item = self.parse_search_item(search_by_keyword=search_by_keyword, a_tag=a)
            if item is not None:  # Avoid adding None values for existing items
                search_items.append(item)

        return search_items

    def parse_search_item(self, search_by_keyword, a_tag):
        # Check if the item already exists to avoid duplicates
        if search_by_keyword.search_type == 'books':
            item, created = BookSearchByKeywordItem.objects.get_or_create(
                search_by_keyword=search_by_keyword,
                title=a_tag.text.strip(),
                defaults={'url': self.base_url + a_tag['href']}
            )
            return item if created else None  # Return only if it's a new item
        elif search_by_keyword.search_type == 'groups':
            item, created = GroupSearchByKeywordItem.objects.get_or_create(
                search_by_keyword=search_by_keyword,
                title=a_tag.text.strip(),
                defaults={'url': self.base_url + a_tag['href']}
            )
            return item if created else None

    def parse_book_detail(self, url):
        response = self.request_to_target_url(url=url)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', attrs={'class': 'Text Text__title1'}).text
        description = soup.find('div', attrs={'class': 'DetailsLayoutRightParagraph__widthConstrained'}).find_next(
            'span').text
        thumbnail = soup.find('img', attrs={'class': 'ResponsiveImage', 'role': 'presentation'})['src']
        author, _ = self.parse_author(soup=soup)

        # Check if the book already exists to avoid duplicates
        book, created = Book.objects.get_or_create(
            author=author,
            title=title,
            defaults={
                'description': description,
                'thumbnail': thumbnail,
            }
        )

        genres = self.parse_genre(soup=soup)

        if created:  # Add genres only for newly created books
            for genre in genres:
                BookGenre.objects.get_or_create(book=book, genre=genre)

        return book, genres

    def parse_author(self, soup):
        fullname = soup.find('span', attrs={'class': 'ContributorLink__name'}).text
        return Author.objects.get_or_create(fullname=fullname)

    def parse_genre(self, soup):
        genres = list()
        genre_soup = soup.find('ul', attrs={'class': 'CollapsableList', 'aria-label': 'Top genres for this book'})

        if genre_soup:  # Check if genre_soup is not None
            for genre in genre_soup.findAll('span', attrs={'class': 'Button__labelItem'}):
                if genre.text != '...more':
                    new_genre, _ = Genre.objects.get_or_create(title=genre.text)
                    genres.append(new_genre)
        else:
            logger.warning('No genres found on the page.')

        return genres

    def parse_group_detail(self, url):
        response = self.request_to_target_url(url=url)
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('div', attrs={'class': 'mainContentFloat'})

        if main_content is None:
            raise ValueError(f"Main content not found for URL: {url}")

        title_element = main_content.findNext('h1')
        if title_element is None:
            raise ValueError(f"Title element not found for URL: {url}")

        title = title_element.text
        thumbnail_element = soup.find('a', attrs={'class': 'groupPicLink'}).find_next('img')

        if thumbnail_element is None:
            raise ValueError(f"Thumbnail element not found for URL: {url}")

        thumbnail = thumbnail_element['src']

        group, created = Group.objects.get_or_create(
            title=title,
            defaults={'thumbnail': thumbnail}
        )

        return group
