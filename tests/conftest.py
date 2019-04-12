import random
import string

import pytest
from django.utils.encoding import force_text
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


def random_string(n):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(n)
    )


def random_name(n):
    words = ''.join(random.choice(string.ascii_lowercase + ' ') for _ in range(n)).strip().split(' ')
    return '-'.join([x.capitalize() for x in words])


@pytest.yield_fixture(scope='session')
def driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.headless = True
    try:
        b = webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        pytest.skip(force_text(e))
    else:
        yield b
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
