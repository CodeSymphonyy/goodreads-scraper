from abc import abstractmethod
from django.db import models
from django.conf import settings


# Create your models here.


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        abstract = True

    @abstractmethod
    def __str__(self):
        raise NotImplementedError('Implement __str__ method')


class Author(BaseModel):
    fullname = models.CharField(max_length=250)

    class Meta:
        verbose_name = 'Author'
        verbose_name_plural = 'Authors'

    def __str__(self):
        return self.fullname


class Genre(BaseModel):
    title = models.CharField(max_length=250)

    class Meta:
        verbose_name = 'Genre'
        verbose_name_plural = 'Genres'

    def __str__(self):
        return self.title


class Book(BaseModel):
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    description = models.TextField()
    thumbnail = models.TextField()

    class Meta:
        verbose_name = 'Book'
        verbose_name_plural = 'Books'

    def __str__(self):
        return self.title


class BookGenre(BaseModel):
    book = models.ForeignKey(Book, related_name='book_genres', on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, related_name='book_genres', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Book Genre'
        verbose_name_plural = 'Book Genres'

    def __str__(self):
        return f'{self.book.title}({self.genre.title})'


class Group(BaseModel):
    title = models.CharField(max_length=250)
    thumbnail = models.TextField()

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self):
        return self.title


class Keyword(BaseModel):
    title = models.CharField(max_length=250)

    class Meta:
        verbose_name = 'Keyword'
        verbose_name_plural = 'Keywords'

    def __str__(self):
        return self.title


class SearchByKeyword(BaseModel):
    keyword = models.ForeignKey(Keyword, related_name='searches', on_delete=models.CASCADE)
    search_type = models.CharField(max_length=250, default=settings.GOOD_READS_DEFAULT_SEARCH_TYPE)
    page_count = models.IntegerField(default=settings.GOOD_READS_DEFAULT_SEARCH_PAGE_COUNT)
    status = models.CharField(max_length=50, default='Pending')  # New field to track status
    processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Search By Keyword'
        verbose_name_plural = 'Search By Keywords'

    def __str__(self):
        return self.keyword.title


class BookSearchByKeywordItem(BaseModel):
    search_by_keyword = models.ForeignKey(
        SearchByKeyword,
        related_name='book_search_by_keyword_items',
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(
        Book,
        related_name='book_search_by_keyword_items',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    url = models.TextField()
    is_scraped = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Book Search By Keyword Item'
        verbose_name_plural = 'Books Search By Keyword Items'

    def __str__(self):
        return f'{self.title}({self.search_by_keyword.keyword.title})'


class GroupSearchByKeywordItem(BaseModel):
    search_by_keyword = models.ForeignKey(
        SearchByKeyword,
        related_name='group_search_by_keyword_items',
        on_delete=models.CASCADE
    )
    group = models.ForeignKey(
        Group,
        related_name='group_search_by_keyword_items',
        blank=True,
        null=True,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    url = models.TextField()
    is_scraped = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Group Search By Keyword Item'
        verbose_name_plural = 'Group Search By Keyword Items'

    def __str__(self):
        return f'{self.title}({self.search_by_keyword.keyword.title})'


class TaskStatus(models.Model):
    task_name = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50, default='pending')
    last_run_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.task_name}: {self.status}'
