# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django import forms

from django_select2.forms import (
    HeavySelect2MultipleWidget, HeavySelect2Widget, Select2MultipleWidget,
    Select2Widget
)
from tests.testapp import models


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
    genres = forms.ModelMultipleChoiceField(widget=HeavySelect2MultipleWidget(
        queryset=models.Genre.objects.all(),
        search_fields=['title'],
    ), queryset=models.Genre.objects.all())


class AlbumModelForm(forms.ModelForm):
    class Meta:
        model = models.Album
        fields = (
            'title',
            'artist',
        )


class AlbumForm(forms.Form):
    title = forms.CharField(max_length=255)
    artist = forms.ModelChoiceField(widget=HeavySelect2Widget(
        model=models.Artist,
        search_fields=['title']
    ), queryset=models.Artist.objects.all())


class Select2WidgetForm(forms.Form):
    NUMBER_CHOICES = [
        (1, 'One'),
        (2, 'Two'),
        (3, 'Three'),
        (4, 'Four'),
    ]
    number = forms.ChoiceField(widget=Select2Widget(), choices=NUMBER_CHOICES)


class HeavySelect2WidgetForm(forms.Form):
    heavy_number = forms.ChoiceField(widget=HeavySelect2Widget(data_view='heavy_data'))


class HeavySelect2MultipleWidgetForm(forms.Form):
    heavy_number = forms.MultipleChoiceField(widget=HeavySelect2MultipleWidget(data_view='heavy_data'))
