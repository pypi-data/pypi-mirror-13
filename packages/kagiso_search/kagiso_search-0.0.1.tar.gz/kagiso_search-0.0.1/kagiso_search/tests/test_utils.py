from django.test import TestCase
from wagtail.wagtailcore.models import Page

from ..utils import pg_full_text_search


class PGFullTextSearchTestCase(TestCase):

    def test_search_no_results_found(self):
        result = pg_full_text_search('Justin Bieber')

        assert list(result) == []

    def test_search_multiple_results_found(self):
        home_page = Page.objects.get(slug='home')
        bieber_article_1 = Page(
            title='Justin Bieber',
            slug='justin-bieber'
        )
        bieber_article_2 = Page(
            title='Justin Bieber Again',
            slug='justin-bieber-again'
        )
        home_page.add_child(instance=bieber_article_1)
        home_page.add_child(instance=bieber_article_2)

        result = pg_full_text_search('Justin Bieber')

        assert list(result) == [bieber_article_1, bieber_article_2]
