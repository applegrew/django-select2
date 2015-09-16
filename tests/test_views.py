# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.core import signing
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_text

from tests.testapp.forms import AlbumModelSelect2WidgetForm


class TestAutoResponseView(object):
    def test_get(self, client, artists):
        artist = artists[0]
        form = AlbumModelSelect2WidgetForm()
        assert form.as_p()
        field_id = signing.dumps(id(form.fields['artist'].widget))
        url = reverse('django_select2-json')
        response = client.get(url, {'field_id': field_id, 'term': artist.title})
        assert response.status_code == 200
        data = json.loads(response.content.decode('utf-8'))
        assert data['results']
        assert {'id': artist.pk, 'text': smart_text(artist)} in data['results']

    def test_no_field_id(self, client, artists):
        artist = artists[0]
        url = reverse('django_select2-json')
        response = client.get(url, {'term': artist.title})
        assert response.status_code == 404

    def test_wrong_field_id(self, client, artists):
        artist = artists[0]
        url = reverse('django_select2-json')
        response = client.get(url, {'field_id': 123, 'term': artist.title})
        assert response.status_code == 404

    def test_field_id_not_found(self, client, artists):
        artist = artists[0]
        field_id = signing.dumps(123456789)
        url = reverse('django_select2-json')
        response = client.get(url, {'field_id': field_id, 'term': artist.title})
        assert response.status_code == 404
