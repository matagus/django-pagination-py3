from django.core.paginator import Paginator
from django.http import Http404
from django.http import HttpRequest as DjangoHttpRequest
from django.http import QueryDict
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

from pagination.templatetags.pagination_tags import paginate


class PaginateTestCase(TestCase):
    def test_first_page_pagination(self):
        p = Paginator(range(15), 2)
        pg = paginate({"paginator": p, "page_obj": p.page(1)})
        self.assertEqual(pg["pages"], [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(pg["records"]["first"], 1)
        self.assertEqual(pg["records"]["last"], 2)

    def test_last_page_pagination(self):
        p = Paginator(range(15), 2)
        pg = paginate({"paginator": p, "page_obj": p.page(8)})
        self.assertEqual(pg["pages"], [1, 2, 3, 4, 5, 6, 7, 8])
        self.assertEqual(pg["records"]["first"], 15)
        self.assertEqual(pg["records"]["last"], 15)

    def test_pages(self):
        p = Paginator(range(17), 2)
        pg = paginate({"paginator": p, "page_obj": p.page(1)})
        self.assertEqual(pg["pages"], [1, 2, 3, 4, 5, 6, 7, 8, 9])

        p = Paginator(range(19), 2)
        pg = paginate({"paginator": p, "page_obj": p.page(1)})
        self.assertEqual(pg["pages"], [1, 2, 3, 4, None, 7, 8, 9, 10])

        p = Paginator(range(21), 2)
        pg = paginate({"paginator": p, "page_obj": p.page(1)})
        self.assertEqual(pg["pages"], [1, 2, 3, 4, None, 8, 9, 10, 11])


class OrphansTestCase(TestCase):
    def test_pagination_first_page(self):
        p = Paginator(range(5), 2, 1)
        result = paginate({"paginator": p, "page_obj": p.page(1)})
        self.assertEqual(result["pages"], [1, 2])

    def test_pagination_middle_page(self):
        p = Paginator(range(21), 2, 1)
        pg = paginate({"paginator": p, "page_obj": p.page(1)})
        self.assertEqual(pg["pages"], [1, 2, 3, 4, None, 7, 8, 9, 10])
        self.assertEqual(pg["records"]["first"], 1)
        self.assertEqual(pg["records"]["last"], 2)

    def test_pagination_last_page(self):
        p = Paginator(range(21), 2, 1)
        pg = paginate({"paginator": p, "page_obj": p.page(10)})
        self.assertEqual(pg["pages"], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(pg["records"]["first"], 19)
        self.assertEqual(pg["records"]["last"], 21)


class HttpRequest(DjangoHttpRequest):
    page = 1


class AutopaginateTestCase(TestCase):
    def setUp(self):
        self.request = HttpRequest()
        self.item_list = list(range(21))

    def test_autopaginate_default(self):
        t = Template("{% load pagination_tags %}{% autopaginate var %}{% paginate %}")
        rendered = t.render(Context({"var": self.item_list, "request": self.request}))
        self.assertIn('<div class="pagination">', rendered)

    def test_autopaginate_custom(self):
        t = Template("{% load pagination_tags %}{% autopaginate var 20 %}{% paginate %}")
        rendered = t.render(Context({"var": self.item_list, "request": self.request}))
        self.assertIn('<div class="pagination">', rendered)

    def test_autopaginate_variable(self):
        t = Template("{% load pagination_tags %}{% autopaginate var by %}{% paginate %}")
        rendered = t.render(Context({"var": self.item_list, "by": 20, "request": self.request}))
        self.assertIn('<div class="pagination">', rendered)

    def test_autopaginate_as_variable(self):
        t = Template("{% load pagination_tags %}{% autopaginate var by as foo %}{{ foo }}")
        rendered = t.render(Context({"var": self.item_list, "by": 20, "request": self.request}))
        self.assertEqual(rendered, "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]")

    def test_autopaginate_as_without_variable_name(self):
        with self.assertRaises(TemplateSyntaxError):
            Template("{% load pagination_tags %}{% autopaginate var as %}")

    def test_autopaginate_with_orphans(self):
        t = Template("{% load pagination_tags %}{% autopaginate var 5 2 %}")
        t.render(Context({"var": self.item_list, "request": self.request}))

    def test_autopaginate_rejects_non_integer_orphans(self):
        with self.assertRaises(TemplateSyntaxError):
            Template("{% load pagination_tags %}{% autopaginate var 5 notanint %}")

    def test_autopaginate_rejects_too_many_args(self):
        with self.assertRaises(TemplateSyntaxError):
            Template("{% load pagination_tags %}{% autopaginate var 5 2 extra %}")

    def test_invalid_page_sets_context_flag(self):
        request = HttpRequest()
        request.page = 99
        t = Template("{% load pagination_tags %}{% autopaginate var 5 %}")
        c = Context({"var": range(10), "request": request})
        t.render(c)
        self.assertEqual(c["invalid_page"], True)

    def test_invalid_page_raises_404_when_configured(self):
        request = HttpRequest()
        request.page = 99
        t = Template("{% load pagination_tags %}{% autopaginate var 5 %}")
        c = Context({"var": range(10), "request": request})
        with self.settings(PAGINATION_INVALID_PAGE_RAISES_404=True):
            with self.assertRaises(Http404):
                t.render(c)

    def test_paginate_preserves_query_params_excluding_page(self):
        request = DjangoHttpRequest()
        request.GET = QueryDict("q=foo&page=2")
        p = Paginator(range(50), 10)
        result = paginate({"paginator": p, "page_obj": p.page(2), "request": request})
        self.assertEqual(result["getvars"], "&q=foo")

    def test_paginate_empty_getvars_when_only_page_param(self):
        request = DjangoHttpRequest()
        request.GET = QueryDict("page=2")
        p = Paginator(range(50), 10)
        result = paginate({"paginator": p, "page_obj": p.page(2), "request": request})
        self.assertEqual(result["getvars"], "")

    def test_paginate_adjacent_page_windows(self):
        p = Paginator(range(200), 10)
        pg = paginate({"paginator": p, "page_obj": p.page(9)})
        self.assertIn(4, pg["pages"])
        self.assertIn(5, pg["pages"])
        idx_4 = pg["pages"].index(4)
        idx_5 = pg["pages"].index(5)
        self.assertEqual(idx_5, idx_4 + 1)

    def test_paginate_page_gap_with_ellipsis(self):
        p = Paginator(range(500), 20)
        pg = paginate({"paginator": p, "page_obj": p.page(20)})
        self.assertIn(None, pg["pages"])

    def test_paginate_missing_context_returns_empty(self):
        result = paginate({})
        self.assertEqual(result, {})
