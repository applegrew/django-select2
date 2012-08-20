from django.db import models

class ClassRoom(models.Model):
    number = models.CharField(max_length=4)

    def __unicode__(self):
        return unicode(self.number)

class Dept(models.Model):
    name = models.CharField(max_length=10)
    allotted_rooms = models.ManyToManyField(ClassRoom)

    def __unicode__(self):
        return unicode(self.name)

class Employee(models.Model):
    name = models.CharField(max_length=30)
    salary = models.FloatField()
    dept = models.ForeignKey(Dept)
    manager = models.ForeignKey('Employee', null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)

