from django.test import RequestFactory, TestCase

from pagination.middleware import PaginationMiddleware


class PaginationMiddlewareTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = PaginationMiddleware(get_response=lambda r: None)

    def test_process_request_attaches_page_property(self):
        request = self.factory.get("/")
        self.middleware.process_request(request)
        self.assertEqual(request.page, 1)

    def test_page_from_get_integer(self):
        request = self.factory.get("/", {"page": "3"})
        self.middleware.process_request(request)
        self.assertEqual(request.page, 3)

    def test_page_invalid_string_returns_1(self):
        request = self.factory.get("/", {"page": "abc"})
        self.middleware.process_request(request)
        self.assertEqual(request.page, 1)

    def test_page_none_returns_1(self):
        request = self.factory.get("/")
        request.GET = request.GET.copy()
        request.GET["page"] = None
        self.middleware.process_request(request)
        self.assertEqual(request.page, 1)
