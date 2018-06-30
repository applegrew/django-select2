from django.db import models


class Genre(models.Model):
    title = models.CharField(max_length=50)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Artist(models.Model):
    title = models.CharField(max_length=50, unique=True)
    genres = models.ManyToManyField(Genre)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Album(models.Model):
    title = models.CharField(max_length=255)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    featured_artists = models.ManyToManyField(Artist, blank=True, related_name='featured_album_set')
    primary_genre = models.ForeignKey(Genre, on_delete=models.CASCADE, blank=True, null=True,
                                      related_name='primary_album_set')
    genres = models.ManyToManyField(Genre)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Country(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField(max_length=255)
    country = models.ForeignKey('Country', related_name="cities", on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Groupie(models.Model):
    obsession = models.ForeignKey(Artist, to_field='title', on_delete=models.CASCADE)
