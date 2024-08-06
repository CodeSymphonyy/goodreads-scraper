from django.contrib import admin
from django.contrib.admin import register

from .models import Author, Genre, Book, BookGenre, Group, Keyword, SearchByKeyword, BookSearchByKeywordItem, \
    GroupSearchByKeywordItem


# Register your models here.


def make_activate(modeladmin, request, queryset):
    queryset.update(is_active=True)


def make_deactivate(modeladmin, request, queryset):
    queryset.update(is_active=False)


class BaseAdmin(admin.ModelAdmin):
    actions = (make_activate, make_deactivate)


@register(Author)
class AuthorAdmin(BaseAdmin):
    list_display = ('id', 'fullname', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'fullname')
    list_filter = ('is_active', 'created_at', 'updated_at')
    list_editable = ('is_active', )


@register(Genre)
class GenreAdmin(BaseAdmin):
    list_display = ('id', 'title', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    list_filter = ('is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)


@register(Book)
class BookAdmin(BaseAdmin):
    list_display = ('id', 'title', 'author', 'description', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    list_filter = ('is_active', 'created_at', 'updated_at', 'author')
    list_editable = ('is_active',)


@register(BookGenre)
class BookGenreAdmin(BaseAdmin):
    list_display = ('id', 'book', 'genre', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'book')
    list_filter = ('is_active', 'created_at', 'updated_at', 'book', 'genre')
    list_editable = ('is_active',)


@register(Group)
class GroupAdmin(BaseAdmin):
    list_display = ('id', 'title', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    list_filter = ('is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)


@register(Keyword)
class KeywordAdmin(BaseAdmin):
    list_display = ('id', 'title', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    list_filter = ('is_active', 'created_at', 'updated_at')
    list_editable = ('is_active',)


@register(SearchByKeyword)
class SearchByKeywordAdmin(BaseAdmin):
    list_display = ('id', 'keyword', 'status', 'is_active', 'created_at', 'updated_at')
    list_display_links = ('id', 'keyword')
    list_filter = ('is_active', 'status', 'created_at', 'updated_at', 'keyword')
    list_editable = ('is_active',)


@register(BookSearchByKeywordItem)
class BookSearchByKeywordItemAdmin(BaseAdmin):
    list_display = (
        'id',
        'search_by_keyword',
        'book',
        'is_scraped',
        'title',
        'url',
        'is_active',
        'created_at',
        'updated_at'
    )
    list_display_links = ('id', 'search_by_keyword')
    list_filter = ('is_active', 'is_scraped', 'created_at', 'updated_at', 'search_by_keyword', 'book')
    list_editable = ('is_active',)


@register(GroupSearchByKeywordItem)
class GroupSearchByKeywordItemAdmin(BaseAdmin):
    list_display = (
        'id',
        'search_by_keyword',
        'group',
        'is_scraped',
        'title',
        'url',
        'is_active',
        'created_at',
        'updated_at'
    )
    list_display_links = ('id', 'search_by_keyword')
    list_filter = ('is_active', 'is_scraped', 'created_at', 'updated_at', 'search_by_keyword', 'group')
    list_editable = ('is_active',)
