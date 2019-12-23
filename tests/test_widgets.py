# -*- coding:utf-8 -*-
from __future__ import print_function, unicode_literals

import pytest
from django.urls import reverse
from selenium.common.exceptions import NoSuchElementException


class TestWidgets(object):
    url = ""

    def test_is_hidden_multiple(self):
        from django_select2.widgets import HeavySelect2MultipleWidget
        new_widget = HeavySelect2MultipleWidget(data_url="/")
        assert new_widget.is_hidden is False

    def test_is_hidden(self):
        from django_select2.widgets import HeavySelect2Widget
        new_widget = HeavySelect2Widget(data_url="/")
        assert new_widget.is_hidden is False


class TestSelect2Widget(object):
    url = reverse('select2_widget')

    def test_selecting(self, db, client, live_server, driver):
        driver.get(live_server + self.url)
        dropdown = driver.find_element_by_css_selector('.select2-results')
        assert dropdown.is_displayed() is False
        elem = driver.find_element_by_css_selector('.select2-choice')
        elem.click()
        assert dropdown.is_displayed() is True
        with pytest.raises(NoSuchElementException):
            error = driver.find_element_by_xpath('//body[@JSError]')
            pytest.fail(error.get_attribute('JSError'))


class TestHeavySelect2Widget(object):
    url = reverse('heavy_select2_widget')

    def test_heavy_select(self, db, client, live_server, driver):
        driver.get(live_server + self.url)
        dropdown = driver.find_element_by_css_selector('.select2-results')
        assert dropdown.is_displayed() is False
        elem = driver.find_element_by_css_selector('.select2-choice')
        elem.click()
        assert dropdown.is_displayed() is True
        with pytest.raises(NoSuchElementException):
            error = driver.find_element_by_xpath('//body[@JSError]')
            pytest.fail(error.get_attribute('JSError'))


class TestHeavySelect2MultipleWidget(object):
    url = reverse('heavy_select2_multiple_widget')

    def test_heavy_select_multiple(self, db, client, live_server, driver):
        driver.get(live_server + self.url)
        dropdown = driver.find_element_by_css_selector('.select2-results')
        assert dropdown.is_displayed() is False
        elem = driver.find_element_by_css_selector('.select2-choices')
        elem.click()
        assert dropdown.is_displayed() is True
        with pytest.raises(NoSuchElementException):
            error = driver.find_element_by_xpath('//body[@JSError]')
            pytest.fail(error.get_attribute('JSError'))
