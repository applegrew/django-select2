# -*- coding:utf-8 -*-
from __future__ import print_function, unicode_literals

import json

import pytest
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text
from selenium.common.exceptions import NoSuchElementException

from django_select2.types import NO_ERR_RESP
from tests.testapp.forms import AlbumForm, ArtistForm


class ViewTestMixin(object):
    url = ''

    def test_get(self, client):
        response = client.get(self.url)
        assert response.status_code == 200


class TestAutoModelSelect2TagField(object):
    url = reverse('single_value_model_field')

    def test_no_js_error(self, db, client, live_server, driver, genres):
        driver.get(live_server + self.url)
        with pytest.raises(NoSuchElementException):
            error = driver.find_element_by_xpath('//body[@JSError]')
            pytest.fail(error.get_attribute('JSError'))

    def test_form(self):
        form = ArtistForm()
        assert form


class TestAutoModelSelect2Field(object):
    def test_form(self, client, artists):
        artist = artists[0]
        form = AlbumForm()
        assert form.as_p()
        field_id = form.fields['artist'].widget.widget_id
        url = reverse('django_select2_central_json')
        response = client.get(url, {'field_id': field_id, 'term': artist.title})
        assert response.status_code == 200
        data = json.loads(response.content.decode('utf-8'))
        assert data['results']
        assert {'id': artist.pk, 'text': smart_text(artist)} in data['results']
        assert data['more'] is False
        assert data['err'] == NO_ERR_RESP
