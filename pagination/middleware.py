try:
    from django.utils.deprecation import MiddlewareMixin
    use_django10 = True
except ImportError:
    use_django10 = False


def get_page(self):
    """
    A function which will be monkeypatched onto the request to get the current
    integer representing the current page.
    """
    try:
        return int(self.GET['page'])
    except (KeyError, ValueError, TypeError):
        return 1

if use_django10 is False:
    class PaginationMiddleware(object):
        """
        Inserts a variable representing the current page onto the request object if
        it exists in either **GET** or **POST** portions of the request.
        """

        def process_request(self, request):
            request.__class__.page = property(get_page)
else:
    class PaginationMiddleware(MiddlewareMixin):
        """
        Inserts a variable representing the current page onto the request object if
        it exists in either **GET** or **POST** portions of the request.
        """

        def process_request(self, request):
            request.__class__.page = property(get_page)

