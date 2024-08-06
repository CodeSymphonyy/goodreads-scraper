from django.shortcuts import render
from .forms import SearchByKeywordForm
from .tasks import good_reads_search_by_keyword_task


def search_by_keyword_view(request):
    if request.method == 'POST':
        form = SearchByKeywordForm(request.POST)
        if form.is_valid():
            # Trigger the Celery task asynchronously
            result = good_reads_search_by_keyword_task.delay(
                keyword=form.cleaned_data['keyword'],
                search_type=form.cleaned_data['search_type'],
                page_count=form.cleaned_data['page_count'],
            )
            context = {
                'form': form,
                'message': 'Your search is being processed. Please check back later for results.',
                'task_id': result.id
            }
            return render(request, 'goodread/search_by_keyword.html', context)
    else:
        form = SearchByKeywordForm()

    return render(request, 'goodread/search_by_keyword.html', {'form': form})
