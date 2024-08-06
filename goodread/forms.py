from django import forms
from django.conf import settings


class SearchByKeywordForm(forms.Form):

    SEARCH_TYPE_CHOICES = (
        ('books', 'Books'),
        ('groups', 'Groups'),
    )

    keyword = forms.CharField(label='Keyword', max_length=250)
    search_type = forms.CharField(
        label='Search Type',
        widget=forms.Select(choices=SEARCH_TYPE_CHOICES),
        initial=settings.GOOD_READS_DEFAULT_SEARCH_TYPE,
    )
    page_count = forms.IntegerField(
        label='Page Count',
        min_value=1,
        max_value=settings.GOOD_READS_MAXIMUM_SEARCH_PAGE_COUNT,
        initial=settings.GOOD_READS_DEFAULT_SEARCH_PAGE_COUNT,
    )
