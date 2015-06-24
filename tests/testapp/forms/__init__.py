# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms

from django_select2.fields import Select2MultipleWidget
from django_select2.widgets import Select2Widget, HeavySelect2Widget, HeavySelect2MultipleWidget

from tests.testapp import models
from . import fields


class GenreModelForm(forms.ModelForm):
    class Meta:
        model = models.Genre
        fields = (
            'title',
        )


class GenreForm(forms.Form):
    title = forms.CharField(max_length=50)


class ArtistModelForm(forms.ModelForm):
    test = forms.BooleanField('asdf')
    class Meta:
        model = models.Artist
        fields = (
            'title',
            'genres',
        )
        widgets = {
            'genres': Select2MultipleWidget
        }


class ArtistForm(forms.Form):
    title = forms.CharField(max_length=50)
    genres = fields.GenreTagField()


class AlbumModelForm(forms.ModelForm):
    class Meta:
        model = models.Album
        fields = (
            'title',
            'artist',
        )


class AlbumForm(forms.Form):
    title = forms.CharField(max_length=255)
    artist = fields.ArtistField()


class Select2WidgetForm(forms.Form):
    NUMBER_CHOICES = [ (1, 'One'),
                       (2, 'Two'),
                       (3, 'Three'),
                       (4, 'Four') ]
    number = forms.ChoiceField(widget=Select2Widget(), choices=NUMBER_CHOICES)


class HeavySelect2WidgetForm(forms.Form):
    heavy_number = forms.ChoiceField(widget=HeavySelect2Widget(data_view='heavy_data'))


class HeavySelect2MultipleWidgetForm(forms.Form):
    heavy_number = forms.MultipleChoiceField(widget=HeavySelect2MultipleWidget(data_view='heavy_data'))
