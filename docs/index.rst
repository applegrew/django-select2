.. include:: ../README.rst

Installation
------------

Install ``django-select2``

.. code-block:: python

    python3 -m pip install django-select2

Add ``django_select2`` to your ``INSTALLED_APPS`` in your project settings.

Add ``django_select`` to your URL root configuration:

.. code-block:: python

    from django.urls import include, path

    urlpatterns = [
        # … other patterns
        path("select2/", include("django_select2.urls")),
        # … other patterns
    ]

Finally make sure you have a persistent cache backend setup (NOT
:class:`.DummyCache` or :class:`.LocMemCache`), we will use Redis in this
example. Make sure you have a Redis server up and running::

    # Debian
    sudo apt-get install redis-server

    # macOS
    brew install redis

    # install Redis python client
    python3 -m pip install django-redis

Next, add the cache configuration to your ``settings.py`` as follows:

.. code-block:: python

    CACHES = {
        # … default cache config and others
        "select2": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/2",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

    # Tell select2 which cache configuration to use:
    SELECT2_CACHE_BACKEND = "select2"


External Dependencies
---------------------

-  jQuery is not included in the package since it is
   expected that in most scenarios this would already be available.


Quick Start
-----------

Here is a quick example to get you started:

First make sure you followed the installation instructions above.
Once everything is setup, let's start with a simple example.

We have the following model:

.. code-block:: python

    # models.py
    from django.conf import settings
    from django.db import models


    class Book(models.Model):
        author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        co_authors = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='co_authored_by')


Next, we create a model form with custom Select2 widgets.

.. code-block:: python

    # forms.py
    from django import forms
    from django_select2 import forms as s2forms

    from . import models


    class AuthorWidget(s2forms.ModelSelect2Widget):
        search_fields = [
            "username__icontains",
            "email__icontains",
        ]


    class CoAuthorsWidget(s2forms.ModelSelect2MultipleWidget):
        search_fields = [
            "username__icontains",
            "email__icontains",
        ]


    class BookForm(forms.ModelForm):
        class Meta:
            model = models.Book
            fields = "__all__"
            widgets = {
                "author": AuthorWidget,
                "co_authors": CoAuthorsWidget,
            }

A simple class based view will do, to render your form:

.. code-block:: python

    # views.py
    from django.views import generic

    from . import forms, models


    class BookCreateView(generic.CreateView):
        model = models.Book
        form_class = forms.BookForm
        success_url = "/"

Make sure to add the view to your ``urls.py``:

.. code-block:: python

    # urls.py
    from django.urls import include, path

    from . import views

    urlpatterns = [
        # … other patterns
        path("select2/", include("django_select2.urls")),
        # … other patterns
        path("book/create", views.BookCreateView.as_view(), name="book-create"),
    ]


Finally, we need a little template, ``myapp/templates/myapp/book_form.html``

.. code-block:: HTML

    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Create Book</title>
        {{ form.media.css }}
        <style>
            input, select {width: 100%}
        </style>
    </head>
    <body>
        <h1>Create a new Book</h1>
        <form method="POST">
            {% csrf_token %}
            {{ form.as_p }}
            <input type="submit">
        </form>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        {{ form.media.js }}
    </body>
    </html>

Done - enjoy the wonders of Select2!


Changelog
---------

See `Github releases`_.

.. _Github releases: https://github.com/codingjoe/django-select2/releases

All Contents
============

Contents:

.. toctree::
   :maxdepth: 2
   :glob:

   django_select2
   extra
   CONTRIBUTING

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
