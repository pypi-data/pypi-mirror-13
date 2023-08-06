from wagtail.wagtailcore.models import Page


def pg_full_text_search(search_query):
    search_query = search_query.strip()
    sql = ("WITH QUERY AS ("  # noqa
            "SELECT to_tsquery('english', replace(%s, ' ', ' & ')) AS tsquery "  # noqa
            ") "  # noqa
            "SELECT p.*, "  # noqa
            "ts_headline('english', p.title, query.tsquery) AS headline, "  # noqa
            "ts_rank_cd(to_tsvector('english', p.title), query.tsquery) AS rank "  # noqa
            "FROM wagtailcore_page p, query "  # noqa
            "WHERE to_tsvector('english', p.title) @@ query.tsquery AND p.live = true "  # noqa
            "ORDER BY rank DESC, first_published_at DESC")  # noqa
    return Page.objects.raw(sql, [search_query])
