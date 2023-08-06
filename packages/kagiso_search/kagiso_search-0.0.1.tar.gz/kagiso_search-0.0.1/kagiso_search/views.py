from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from wagtail.wagtailsearch.models import Query


from .utils import pg_full_text_search


@never_cache
def search(request):
    search_query = request.GET.get('query')
    page_number = request.GET.get('page', 1)
    search_results = []

    if search_query:
        non_site_scoped_results = pg_full_text_search(search_query)
        for result in non_site_scoped_results:
            # TODO: RawQuerySet cannot call further filter methods like is
            # possible on a regular queryset.
            # http://stackoverflow.com/a/9135752/818951
            # Maybe the below can be done in regular sql
            ancestors = result.get_ancestors()
            if request.site.root_page in ancestors:  # Scope to current site
                specific = result.specific
                specific.headline = result.headline
                search_results.append(specific)

            # Log the query so Wagtail can suggest promoted results
            Query.get(search_query).add_hit()

    paginator = Paginator(search_results, settings.ITEMS_PER_PAGE)
    try:
        page = paginator.page(page_number)
    except EmptyPage:
        # Show empty search page, like Tumblr and co.
        pass

    return render(request, 'kagiso_search/search_results.html', {
        'search_query': search_query,
        'search_results': page,
    })
