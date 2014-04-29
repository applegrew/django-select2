# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import force_text, python_2_unicode_compatible


@python_2_unicode_compatible
class ClassRoom(models.Model):
    number = models.CharField(max_length=4)

    def __str__(self):
        return force_text(self.number)


@python_2_unicode_compatible
class Lab(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return force_text(self.name)


@python_2_unicode_compatible
class Dept(models.Model):
    name = models.CharField(max_length=10)
    allotted_rooms = models.ManyToManyField(ClassRoom)
    allotted_labs = models.ManyToManyField(Lab)

    def __str__(self):
        return force_text(self.name)


@python_2_unicode_compatible
class Employee(models.Model):
    name = models.CharField(max_length=30)
    salary = models.FloatField()
    dept = models.ForeignKey(Dept)
    manager = models.ForeignKey('Employee', null=True, blank=True)

    def __str__(self):
        return force_text(self.name)


@python_2_unicode_compatible
class Word(models.Model):
    word = models.CharField(max_length=15)

    def __str__(self):
        return force_text(self.word)


@python_2_unicode_compatible
class School(models.Model):
    classes = models.ManyToManyField(ClassRoom)


@python_2_unicode_compatible
class Tag(models.Model):
    tag = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return force_text(self.tag)


@python_2_unicode_compatible
class Question(models.Model):
    question = models.CharField(max_length=200)
    description = models.CharField(max_length=800)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return force_text(self.question)


@python_2_unicode_compatible
class KeyValueMap(models.Model):
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=300)

    def __str__(self):
        return u'%s=>%s' % (self.key, self.value)


@python_2_unicode_compatible
class WordList(models.Model):
    kind = models.CharField(max_length=100)
    word = models.ForeignKey(Word, null=True, blank=True, related_name='wordlist_word')
    words = models.ManyToManyField(Word, null=True, blank=True, related_name='wordlist_words')
