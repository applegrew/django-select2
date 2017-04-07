# -*- coding:utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import random
import string
from time import sleep

import pytest
from django.utils.encoding import force_text
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

browsers = {
    'chrome': webdriver.Chrome,
    'firefox': webdriver.Firefox,
    'phantomjs': webdriver.PhantomJS,
}


def random_string(n):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(n)
    )


def random_name(n):
    words = ''.join(random.choice(string.ascii_lowercase + ' ') for _ in range(n)).strip().split(' ')
    return '-'.join([x.capitalize() for x in words])


@pytest.yield_fixture(scope='session', params=sorted(browsers.keys()))
def driver(request):
    if 'DISPLAY' not in os.environ:
        pytest.skip('Test requires display server (export DISPLAY)')

    try:
        b = browsers[request.param]()
    except WebDriverException as e:
        pytest.skip(force_text(e))
    else:
        b.set_window_size(1200, 800)
        yield b
        if request.param == 'chrome':
            # chrome needs a couple of seconds before it can be quit
            sleep(5)
        b.quit()


@pytest.fixture
def genres(db):
    from .testapp.models import Genre

    return Genre.objects.bulk_create(
        [Genre(pk=pk, title=random_string(50)) for pk in range(100)]
    )


@pytest.fixture
def artists(db):
    from .testapp.models import Artist
    return Artist.objects.bulk_create(
        [Artist(pk=pk, title=random_string(50)) for pk in range(100)]
    )


@pytest.fixture
def countries(db):
    from .testapp.models import Country
    return Country.objects.bulk_create(
        [Country(pk=pk, name=random_name(random.randint(10, 20))) for pk in range(10)]
    )


@pytest.fixture
def cities(db, countries):
    from .testapp.models import City
    return City.objects.bulk_create(
        [City(pk=pk, name=random_name(random.randint(5, 15)), country=random.choice(countries)) for pk in range(100)]
    )
