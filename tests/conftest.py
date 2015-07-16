# -*- coding:utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os

import pytest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

browsers = {
    'firefox': webdriver.Firefox,
    'chrome': webdriver.Chrome,
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
