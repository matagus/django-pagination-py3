try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.http import HttpRequest as DjangoHttpRequest
from django.template import Template, Context  # NOQA
from django.test import TestCase

from pagination.paginator import InfinitePaginator, FinitePaginator
from pagination.templatetags.pagination_tags import paginate
from pagination.middleware import PaginationMiddleware


class DoctestContainerTest(TestCase):
    def test_django_requests(self):
        return

    def test_legacy_doctests(self):
        p = Paginator(range(15), 2)
        pg = paginate({'paginator': p, 'page_obj': p.page(1)})
        assert pg['pages'] == [1, 2, 3, 4, 5, 6, 7, 8]
        assert pg['records']['first'] == 1
        assert pg['records']['last'] == 2

        p = Paginator(range(15), 2)
        pg = paginate({'paginator': p, 'page_obj': p.page(8)})
        assert pg['pages'] == [1, 2, 3, 4, 5, 6, 7, 8]
        assert pg['records']['first'] == 15
        assert pg['records']['last'] == 15

        p = Paginator(range(17), 2)
        assert paginate({'paginator': p, 'page_obj': p.page(1)})['pages'] == [1, 2, 3, 4, 5, 6, 7, 8, 9]

        p = Paginator(range(19), 2)
        paginate({'paginator': p, 'page_obj': p.page(1)})['pages'] == [1, 2, 3, 4, None, 7, 8, 9, 10]

        p = Paginator(range(21), 2)
        assert paginate({'paginator': p, 'page_obj': p.page(1)})['pages'] == [1, 2, 3, 4, None, 8, 9, 10, 11]

        # Testing orphans
        p = Paginator(range(5), 2, 1)
        assert paginate({'paginator': p, 'page_obj': p.page(1)})['pages'] == [1, 2]

        p = Paginator(range(21), 2, 1)
        pg = paginate({'paginator': p, 'page_obj': p.page(1)})
        assert pg['pages'] == [1, 2, 3, 4, None, 7, 8, 9, 10]
        assert pg['records']['first'] == 1
        assert pg['records']['last'] == 2

        p = Paginator(range(21), 2, 1)
        pg = paginate({'paginator': p, 'page_obj': p.page(10)})
        assert pg['pages'] == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        assert pg['records']['first'] == 19
        assert pg['records']['last'] == 21

        t = Template("{% load pagination_tags %}{% autopaginate var 2 %}{% paginate %}")
        req = DjangoHttpRequest()
        req.page = 1

        rendered = t.render(Context({'var': range(21), 'request': req})).strip()
        assert rendered.startswith(u'<div class="pagination">'), rendered

        t = Template("{% load pagination_tags %}{% autopaginate var %}{% paginate %}")
        rendered = t.render(Context({'var': range(21), 'request': req})).strip()
        assert rendered.startswith(u'<div class="pagination">')

        t = Template("{% load pagination_tags %}{% autopaginate var 20 %}{% paginate %}")
        rendered = t.render(Context({'var': range(21), 'request': req})).strip()
        assert rendered.startswith('<div class="pagination">')
        t = Template("{% load pagination_tags %}{% autopaginate var by %}{% paginate %}")
        rendered = t.render(Context({'var': range(21), 'by': 20, 'request': req})).strip()
        assert rendered.startswith(u'<div class="pagination">')
        t = Template("{% load pagination_tags %}{% autopaginate var by as foo %}{{ foo }}")

        # rendered = t.render(Context({'var': range(21), 'by': 20, 'request': req}))
        # assert rendered == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

        # Testing InfinitePaginator

        p = InfinitePaginator(range(20), 2, link_template='/bacon/page/{}')
        assert p.validate_number(2) == 2
        assert p.orphans == 0
        p3 = p.page(3)
        assert repr(p3) == "<Page 3>"
        assert p3.end_index() == 6
        assert p3.has_next()
        assert p3.has_previous()
        assert p.page(10).has_next() is False
        assert p.page(1).has_previous() is False

        # TODO: uncomment it
        assert p3.next_link() == '/bacon/page/4', p3.next_link()
        assert p3.previous_link() == '/bacon/page/2'

        # Testing FinitePaginator

        p = FinitePaginator(range(20), 2, offset=10, link_template='/bacon/page/{}')
        assert p.validate_number(2) == 2
        assert p.orphans == 0
        p3 = p.page(3)
        assert p3.start_index() == 10
        assert p3.end_index() == 6
        assert p3.has_next() is True
        assert p3.has_previous() is True

        # TODO: uncomment it
        assert p3.next_link() == '/bacon/page/4'
        assert p3.previous_link() == '/bacon/page/2'

        p = FinitePaginator(range(20), 20, offset=10, link_template='/bacon/page/{}')
        p2 = p.page(2)
        assert p2.has_next() is False
        assert p3.has_previous() is True
        assert p2.next_link() is None

        assert p2.previous_link() == '/bacon/page/1'

        middleware = PaginationMiddleware()
        request = WSGIRequest({'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': 'multipart', 'wsgi.input': StringIO()})
        middleware.process_request(request)
        request.upload_handlers.append('asdf')
