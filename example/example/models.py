from django.conf import settings
from django.db import models


class Book(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    co_authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="co_authored_by"
    )
