# Getting started

django-pagination-py3 is a set of utilities for creating robust pagination tools throughout a django application.

It is a fork of the original django-pagination, which was created by Eric Holscher. This fork is intended to update
the original code to work with Python 3+ and Django 4+. Please take into account that no new features will be added
to this package, only bug fixes and compatibility updates.

## Installation

Install using pip:

```bash
pip install django-pagination-py3
```

## Usage

``django-pagination-py3`` allows for easy Digg-style pagination without modifying your views.

There are really 5 steps to setting it up with your projects (not including installation, which is covered in
[Installation](#installation) above.

1. List this application in the ``INSTALLED_APPS`` portion of your settings file. Your settings file might look
something like::

```python
       INSTALLED_APPS = (
           # ...
           'pagination',
       )
```


2. Install the pagination middleware. Your settings file might look something like::

```python
       MIDDLEWARE_CLASSES = (
           # ...
           'pagination.middleware.PaginationMiddleware',
       )
```


3. Add this line at the top of your template to load the pagination tags:

```html
       {% load pagination_tags %}
```

4. Decide on a variable that you would like to paginate, and use the autopaginate tag on that variable before
iterating over it. This could take one of two forms (using the canonical ``object_list`` as an example variable):

```html
       {% autopaginate object_list %}
```

This assumes that you would like to have the default 20 results per page. If you would like to specify your own amount
of results per page, you can specify that like so:

```html
       {% autopaginate object_list 10 %}
```

Note that this replaces ``object_list`` with the list for the current page, so you can iterate over the ``object_list``
like you normally would.


5. Now you want to display the current page and the available pages, so somewhere after having used autopaginate, use
the paginate inclusion tag:

```html
       {% paginate %}
```

This does not take any arguments, but does assume that you have already called autopaginate, so make sure to do so
first.

That's it!  You have now paginated ``object_list`` and given users of the sitea a way to navigate between the
different pages--all without touching your views.


#### A Note About Uploads

It is important, when using django-pagination-py3 in conjunction with file uploads, to be aware of when ``request.page``
is accessed.  As soon as ``request.page`` is accessed, ``request.upload_handlers`` is frozen and cannot be altered in
any way.  It's a good idea to access the ``page`` attribute on the request object as late as possible in your views.


#### Optional Settings

In django-pagination-py3, there are no required settings.  There are, however, a small set of optional settings useful
for changing the default behavior of the pagination tags.  Here's an overview:

``PAGINATION_DEFAULT_PAGINATION``
    The default amount of items to show on a page if no number is specified.

``PAGINATION_DEFAULT_WINDOW``
    The number of items to the left and to the right of the current page to display (accounting for ellipses).

``PAGINATION_DEFAULT_ORPHANS``
    The number of orphans allowed.  According to the Django documentation, orphans are defined as::

    The minimum number of items allowed on the last page, defaults to zero.

``PAGINATION_INVALID_PAGE_RAISES_404``
    Determines whether an invalid page raises an ``Http404`` or just sets the ``invalid_page`` context variable.
    ``True`` does the former and ``False`` does the latter.


## Repository and Issue Tracker

 * [Repository](https://github.com/matagus/django-pagination-py3)
 * [Issue Tracker](https://github.com/matagus/django-pagination-py3/issues)

## PyPi

 * [Pypi](https://pypi.org/project/django-pagination-py3/)
