# -*- coding:utf-8 -*-
from __future__ import print_function, unicode_literals

import pytest
from django.core.urlresolvers import reverse
from model_mommy import mommy
from selenium.common.exceptions import NoSuchElementException


class ViewTestMixin(object):
    url = ''

    def test_get(self, client):
        response = client.get(self.url)
        assert response.status_code == 200


@pytest.fixture
def genres(db):
    mommy.make('testapp.Genre', _quantity=100)


class TestAutoModelSelect2TagField(object):
    url = reverse('single_value_model_field')

    def test_no_js_error(self, db, client, live_server, driver, genres):
        driver.get(live_server + self.url)
        with pytest.raises(NoSuchElementException):
            error = driver.find_element_by_xpath('//body[@JSError]')
            pytest.fail(error.get_attribute('JSError'))
