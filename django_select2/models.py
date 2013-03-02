from django.db import models

class KeyMap(models.Model):
    key = models.CharField(max_length=40, unique=True)
    value = models.CharField(max_length=100)
    accessed_on = models.DateTimeField(auto_now_add=True, auto_now=True)

    def __unicode__(self):
        return unicode("%s => %s" % (self.key, self.value))
