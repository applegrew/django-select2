# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import collections
import json

import pytest
from django.core import signing
from django.core.urlresolvers import reverse
from django.db.models import QuerySet
from django.utils.encoding import force_text
from model_mommy import mommy
from selenium.common.exceptions import NoSuchElementException
from six import text_type

from django_select2.cache import cache
from django_select2.forms import (
    HeavySelect2Widget, ModelSelect2TagWidget, ModelSelect2Widget,
    Select2Widget
)
from tests.testapp import forms
from tests.testapp.forms import (
    NUMBER_CHOICES, HeavySelect2MultipleWidgetForm, TitleModelSelect2Widget
)
from tests.testapp.models import Genre


class TestSelect2Mixin(object):
    url = reverse('select2_widget')
    form = forms.AlbumSelect2WidgetForm()
    widget_cls = Select2Widget

    def test_initial_form_class(self):
        widget = self.widget_cls(attrs={'class': 'my-class'})
        assert 'my-class' in widget.render('name', None)
        assert 'django-select2' in widget.render('name', None)

    def test_allow_clear(self, db):
        required_field = self.form.fields['artist']
        assert required_field.required is True
        assert 'data-allow-clear="true"' not in required_field.widget.render('artist', None)
        assert 'data-allow-clear="false"' in required_field.widget.render('artist', None)
        assert '<option></option>' not in required_field.widget.render('artist', None)

        not_required_field = self.form.fields['primary_genre']
        assert not_required_field.required is False
        assert 'data-allow-clear="true"' in not_required_field.widget.render('primary_genre', None)
        assert 'data-allow-clear="false"' not in not_required_field.widget.render('primary_genre',
                                                                                  None)
        assert 'data-placeholder' in not_required_field.widget.render('primary_genre', None)
        assert '<option></option>' in not_required_field.widget.render('primary_genre', None)

    def test_no_js_error(self, db, live_server, driver):
        driver.get(live_server + self.url)
        with pytest.raises(NoSuchElementException):
            error = driver.find_element_by_xpath('//body[@JSError]')
            pytest.fail(error.get_attribute('JSError'))

    def test_selecting(self, db, live_server, driver):
        driver.get(live_server + self.url)
        with pytest.raises(NoSuchElementException):
            driver.find_element_by_css_selector('.select2-results')
        elem = driver.find_element_by_css_selector('.select2-selection')
        elem.click()
        results = driver.find_element_by_css_selector('.select2-results')
        assert results.is_displayed() is True
        elem = results.find_element_by_css_selector('.select2-results__option')
        elem.click()

        with pytest.raises(NoSuchElementException):
            error = driver.find_element_by_xpath('//body[@JSError]')
            pytest.fail(error.get_attribute('JSError'))

    def test_data_url(self):
        with pytest.raises(ValueError):
            HeavySelect2Widget()

        widget = HeavySelect2Widget(data_url='/foo/bar')
        assert widget.get_url() == '/foo/bar'


class TestHeavySelect2Mixin(TestSelect2Mixin):
    url = reverse('heavy_select2_widget')
    form = forms.HeavySelect2WidgetForm(initial={'primary_genre': [1]})
    widget_cls = HeavySelect2Widget

    def test_initial_form_class(self):
        widget = self.widget_cls(data_view='heavy_data', attrs={'class': 'my-class'})
        assert 'my-class' in widget.render('name', None)
        assert 'django-select2' in widget.render('name', None)
        assert 'django-select2-heavy' in widget.render('name', None), widget.render('name', None)

    def test_selected_option(self, db):
        not_required_field = self.form.fields['primary_genre']
        assert not_required_field.required is False
        assert '<option value="1" selected="selected">One</option>' in \
               not_required_field.widget.render('primary_genre', 1, choices=NUMBER_CHOICES), \
            not_required_field.widget.render('primary_genre', 1, choices=NUMBER_CHOICES)

    def test_many_selected_option(self, db, genres):
        field = HeavySelect2MultipleWidgetForm().fields['genres']
        widget_output = field.widget.render(
            'genres', [1, 2],
            choices=NUMBER_CHOICES)
        selected_option = '<option value="{pk}" selected="selected">{value}</option>'.format(pk=1, value='One')
        selected_option2 = '<option value="{pk}" selected="selected">{value}</option>'.format(pk=2, value='Two')

        assert selected_option in widget_output, widget_output
        assert selected_option2 in widget_output


class TestModelSelect2Mixin(TestHeavySelect2Mixin):
    form = forms.AlbumModelSelect2WidgetForm(initial={'primary_genre': 1})

    @pytest.fixture(autouse=True)
    def genres(self, db):
        return mommy.make(Genre, 100)

    def test_selected_option(self, db, genres):
        genre = genres[0]
        genre2 = genres[1]
        not_required_field = self.form.fields['primary_genre']
        assert not_required_field.required is False
        widget_output = not_required_field.widget.render(
            'primary_genre', genre.pk)
        selected_option = '<option value="{pk}" selected="selected">{value}</option>'.format(
            pk=genre.pk, value=force_text(genre))
        unselected_option = '<option value="{pk}">{value}</option>'.format(
            pk=genre2.pk, value=force_text(genre2))

        assert selected_option in widget_output, widget_output
        assert unselected_option not in widget_output

    def test_get_queryset(self):
        widget = ModelSelect2Widget()
        with pytest.raises(NotImplementedError):
            widget.get_queryset()
        widget.model = Genre
        assert isinstance(widget.get_queryset(), QuerySet)
        widget.model = None
        widget.queryset = Genre.objects.all()
        assert isinstance(widget.get_queryset(), QuerySet)

    def test_get_search_fields(self):
        widget = ModelSelect2Widget()
        with pytest.raises(NotImplementedError):
            widget.get_search_fields()

        widget.search_fields = ['title__icontains']
        assert isinstance(widget.get_search_fields(), collections.Iterable)
        assert all(isinstance(x, text_type) for x in widget.get_search_fields())

    def test_filter_queryset(self, genres):
        widget = TitleModelSelect2Widget(queryset=Genre.objects.all())
        assert widget.filter_queryset(genres[0].title[:3]).exists()

        widget = TitleModelSelect2Widget(search_fields=['title__icontains'],
                                         queryset=Genre.objects.all())
        qs = widget.filter_queryset(" ".join([genres[0].title[:3], genres[0].title[3:]]))
        assert qs.exists()



    def test_model_kwarg(self):
        widget = ModelSelect2Widget(model=Genre, search_fields=['title__icontains'])
        genre = Genre.objects.last()
        result = widget.filter_queryset(genre.title)
        assert result.exists()

    def test_queryset_kwarg(self):
        widget = ModelSelect2Widget(queryset=Genre.objects.all(), search_fields=['title__icontains'])
        genre = Genre.objects.last()
        result = widget.filter_queryset(genre.title)
        assert result.exists()

    def test_ajax_view_registration(self, client):
        widget = ModelSelect2Widget(queryset=Genre.objects.all(), search_fields=['title__icontains'])
        widget.render('name', 'value')
        url = reverse('django_select2-json')
        genre = Genre.objects.last()
        response = client.get(url, data=dict(field_id=signing.dumps(id(widget)), term=genre.title))
        assert response.status_code == 200, response.content
        data = json.loads(response.content.decode('utf-8'))
        assert data['results']
        assert genre.pk in [result['id'] for result in data['results']]

    def test_render(self):
        widget = ModelSelect2Widget(queryset=Genre.objects.all())
        widget.render('name', 'value')
        cached_widget = cache.get(widget._get_cache_key())
        assert cached_widget['max_results'] == widget.max_results
        assert cached_widget['search_fields'] == widget.search_fields
        qs = widget.get_queryset()
        assert isinstance(cached_widget['queryset'][0], qs.__class__)
        assert text_type(cached_widget['queryset'][1]) == text_type(qs.query)


class TestHeavySelect2TagWidget(TestHeavySelect2Mixin):

    def test_tag_attrs(self):
        widget = ModelSelect2TagWidget(queryset=Genre.objects.all(), search_fields=['title__icontains'])
        output = widget.render('name', 'value')
        assert 'data-minimum-input-length="1"' in output
        assert 'data-tags="true"' in output
        assert 'data-token-separators' in output
