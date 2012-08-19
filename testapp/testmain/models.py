from django.db import models

class Dept(models.Model):
    name = models.CharField(max_length=10)

    def __unicode__(self):
        return unicode(self.name)

class Employee(models.Model):
    name = models.CharField(max_length=30)
    salary = models.FloatField()
    dept = models.ForeignKey(Dept)
    manager = models.ForeignKey('Employee', null=True, blank=True)

    def __unicode__(self):
        return unicode(self.name)
