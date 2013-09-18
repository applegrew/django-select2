from django.db import models

class ClassRoom(models.Model):
    number = models.CharField(max_length=4)

    def __unicode__(self):
        return str(self.number)

class Lab(models.Model):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return str(self.name)

class Dept(models.Model):
    name = models.CharField(max_length=10)
    allotted_rooms = models.ManyToManyField(ClassRoom)
    allotted_labs = models.ManyToManyField(Lab)

    def __unicode__(self):
        return str(self.name)

class Employee(models.Model):
    name = models.CharField(max_length=30)
    salary = models.FloatField()
    dept = models.ForeignKey(Dept)
    manager = models.ForeignKey('Employee', null=True, blank=True)

    def __unicode__(self):
        return str(self.name)

class Word(models.Model):
    word = models.CharField(max_length=15)

    def __unicode__(self):
        return str(self.word)


class School(models.Model):
    classes = models.ManyToManyField(ClassRoom)

class Tag(models.Model):
    tag = models.CharField(max_length=10, unique=True)

    def __unicode__(self):
        return str(self.tag)

class Question(models.Model):
    question = models.CharField(max_length=200)
    description = models.CharField(max_length=800)
    tags = models.ManyToManyField(Tag)

    def __unicode__(self):
        return str(self.question)

class KeyValueMap(models.Model):
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=300)

    def __unicode__(self):
        return '%s=>%s' % (self.key, self.value)

class WordList(models.Model):
    kind = models.CharField(max_length=100)
    word = models.ForeignKey(Word, null=True, blank=True, related_name='wordlist_word')
    words = models.ManyToManyField(Word, null=True, blank=True, related_name='wordlist_words')
