# -*- coding:utf-8 -*-
from __future__ import print_function, unicode_literals

import json
from collections import Iterable

import pytest
from django.core import signing
from django.core.urlresolvers import reverse
from django.db.models import QuerySet
from model_mommy import mommy
from selenium.common.exceptions import NoSuchElementException
from six import text_type

from django_select2 import AutoHeavySelect2Widget
from django_select2.cache import cache
from tests.testapp.models import Genre


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


class TestHeavySelect2Mixin(object):
    @pytest.fixture(autouse=True)
    def genres(self, db):
        mommy.make(Genre, 100)

    def test_get_queryset(self):
        widget = AutoHeavySelect2Widget()
        with pytest.raises(NotImplementedError):
            widget.get_queryset()
        widget.model = Genre
        assert isinstance(widget.get_queryset(), QuerySet)
        widget.model = None
        widget.queryset = Genre.objects.all()
        assert isinstance(widget.get_queryset(), QuerySet)

    def test_get_search_fields(self):
        widget = AutoHeavySelect2Widget()
        with pytest.raises(NotImplementedError):
            widget.get_search_fields()

        widget.search_fields = ['title__icontains']
        assert isinstance(widget.get_search_fields(), Iterable)
        assert all(isinstance(x, text_type) for x in widget.get_search_fields())

    def test_model_kwarg(self):
        widget = AutoHeavySelect2Widget(model=Genre, search_fields=['title__icontains'])
        genre = Genre.objects.last()
        result = widget.filter_queryset(genre.title)
        assert result.exists()

    def test_queryset_kwarg(self):
        widget = AutoHeavySelect2Widget(queryset=Genre.objects, search_fields=['title__icontains'])
        genre = Genre.objects.last()
        result = widget.filter_queryset(genre.title)
        assert result.exists()

    def test_widget_id(self):
        widget = AutoHeavySelect2Widget()
        widget.render('name', 'value')
        assert widget.widget_id
        assert signing.loads(widget.widget_id) == id(widget)

    def test_render(self):
        widget = AutoHeavySelect2Widget()
        widget.render('name', 'value')
        cached_widget = cache.get(widget._get_cache_key())
        assert isinstance(cached_widget, AutoHeavySelect2Widget)
        assert cached_widget.widget_id == widget.widget_id

    def test_ajax_view_registration(self, client):
        widget = AutoHeavySelect2Widget(queryset=Genre.objects, search_fields=['title__icontains'])
        widget.render('name', 'value')
        url = reverse('django_select2_central_json')
        genre = Genre.objects.last()
        response = client.get(url, data=dict(field_id=widget.widget_id, term=genre.title))
        assert response.status_code == 200, response.content
        data = json.loads(response.content.decode('utf-8'))
        assert data['results']
        assert genre.pk in [result['id'] for result in data['results']]
