# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.contrib.admin.sites import AdminSite
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.forms.widgets import Select, SelectMultiple

from django_select2.admin import (
    Select2ModelAdmin, Select2StackedInline, Select2TabularInline,
    Select2Widget
)
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from tests.testapp.models import Album, Genre


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()


class TestSelect2ModelAdmin(object):
    site = AdminSite()

    def test_widgets(self):

        class AlbumModelAdmin(Select2ModelAdmin):
            model = Album
            select2_fields = {
                'artist': {
                    'widget_kwargs': {
                        'search_fields': ['title__icontains'],
                        'attrs': {
                            'style': 'width:250px;',
                            'data-minimum-input-length': 3,
                        }
                    },
                },
                'featured_artists': {
                    'widget_kwargs': {
                        'search_fields': ['title__icontains'],
                        'attrs': {
                            'style': 'width:500px;',
                            'data-minimum-input-length': 2,
                        }
                    },
                },
                'album_type': {
                    'widget_kwargs': {
                        'attrs': {
                            'data-minimum-input-length': 1,
                        }
                    },
                },
            }

        model_admin = AlbumModelAdmin(Album, self.site)
        admin_form = model_admin.get_form(request)
        # check select2 fields
        artist_field = admin_form.base_fields['artist']
        assert isinstance(artist_field.widget, RelatedFieldWidgetWrapper)
        artist_widget = artist_field.widget.widget
        assert isinstance(artist_widget, ModelSelect2Widget)
        assert artist_widget.attrs['data-minimum-input-length'] == 3
        assert artist_widget.attrs['style'] == 'width:250px;'
        featured_artists_field = admin_form.base_fields['featured_artists']
        assert isinstance(
            featured_artists_field.widget, RelatedFieldWidgetWrapper
        )
        featured_artists_widget = featured_artists_field.widget.widget
        assert isinstance(featured_artists_widget, ModelSelect2MultipleWidget)
        assert featured_artists_widget.attrs['data-minimum-input-length'] == 2
        assert featured_artists_widget.attrs['style'] == 'width:500px;'
        album_type_field = admin_form.base_fields['album_type']
        album_type_widget = album_type_field.widget
        assert isinstance(album_type_widget, Select2Widget)
        assert album_type_widget.attrs['data-minimum-input-length'] == 1
        # check non-select2 fields
        primary_genre_field = admin_form.base_fields['primary_genre']
        assert isinstance(
            primary_genre_field.widget, RelatedFieldWidgetWrapper
        )
        assert isinstance(primary_genre_field.widget.widget, Select)
        genres_field = admin_form.base_fields['genres']
        assert isinstance(genres_field.widget, RelatedFieldWidgetWrapper)
        assert isinstance(genres_field.widget.widget, SelectMultiple)


class TestSelect2StackedInline(object):
    site = AdminSite()

    def _test_inline(self, inline_class):

        class InlineAlbumModelAdmin(inline_class):
            model = Album
            fk_name = 'primary_genre'
            select2_fields = {
                'artist': {
                    'widget_kwargs': {
                        'search_fields': ['title__icontains'],
                        'attrs': {
                            'style': 'width:250px;',
                            'data-minimum-input-length': 3,
                        }
                    },
                },
                'featured_artists': {
                    'widget_kwargs': {
                        'search_fields': ['title__icontains'],
                        'attrs': {
                            'style': 'width:500px;',
                            'data-minimum-input-length': 2,
                        }
                    },
                },
            }

        model_admin = InlineAlbumModelAdmin(Genre, self.site)
        admin_form = model_admin.get_formset(request).form
        # check select2 fields
        artist_field = admin_form.base_fields['artist']
        assert isinstance(artist_field.widget, RelatedFieldWidgetWrapper)
        artist_widget = artist_field.widget.widget
        assert isinstance(artist_widget, ModelSelect2Widget)
        assert artist_widget.attrs['data-minimum-input-length'] == 3
        assert artist_widget.attrs['style'] == 'width:250px;'
        featured_artists_field = admin_form.base_fields['featured_artists']
        assert isinstance(
            featured_artists_field.widget, RelatedFieldWidgetWrapper
        )
        featured_artists_widget = featured_artists_field.widget.widget
        assert isinstance(featured_artists_widget, ModelSelect2MultipleWidget)
        assert featured_artists_widget.attrs['data-minimum-input-length'] == 2
        assert featured_artists_widget.attrs['style'] == 'width:500px;'
        # check non-select2 fields
        genres_field = admin_form.base_fields['genres']
        assert isinstance(genres_field.widget, RelatedFieldWidgetWrapper)
        assert isinstance(genres_field.widget.widget, SelectMultiple)

    def test_stacked_inline(self):
        self._test_inline(Select2StackedInline)

    def test_tabular_inline(self):
        self._test_inline(Select2TabularInline)
