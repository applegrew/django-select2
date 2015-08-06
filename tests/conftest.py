# -*- coding:utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os

import pytest
from model_mommy import mommy
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

browsers = {
    # 'firefox': webdriver.Firefox,
    # 'chrome': webdriver.Chrome,
    'phantomjs': webdriver.PhantomJS,
}


@pytest.fixture(scope='session',
                params=browsers.keys())
def driver(request):
    if 'DISPLAY' not in os.environ:
        pytest.skip('Test requires display server (export DISPLAY)')

    try:
        b = browsers[request.param]()
    except WebDriverException as e:
        pytest.skip(e)
    else:
        b.set_window_size(1200, 800)
        request.addfinalizer(lambda *args: b.quit())
        return b


@pytest.fixture
def genres(db):
    return mommy.make('testapp.Genre', _quantity=100)


@pytest.fixture
def artists(db):
    return mommy.make('testapp.Artist', _quantity=100)
