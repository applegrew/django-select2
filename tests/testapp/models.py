# -*- coding:utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Genre(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Artist(models.Model):
    title = models.CharField(max_length=50)
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    featured_artists = models.ManyToManyField(Artist, blank=True, related_name='featured_album_set')
    primary_genre = models.ForeignKey(Genre, on_delete=models.CASCADE, blank=True, null=True,
                                      related_name='primary_album_set')
    genres = models.ManyToManyField(Genre)

    def __str__(self):
        return self.title


@python_2_unicode_compatible
class Country(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey('Country', related_name="cities")

    def __str__(self):
        return self.name
