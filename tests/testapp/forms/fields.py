# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django_select2.fields import (AutoModelSelect2Field,
                                   AutoModelSelect2TagField)
from tests.testapp import models


class GenreTagField(AutoModelSelect2TagField):
    queryset = models.Genre


class ArtistField(AutoModelSelect2Field):
    queryset = models.Artist
