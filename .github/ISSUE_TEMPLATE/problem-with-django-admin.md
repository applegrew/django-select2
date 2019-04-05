---
name: Problem with Django admin
about: You are facing a problem integrating django-select2 into Django's admin interface
title: ''
labels: wontfix
assignees: ''

---

Django-Select2 does NOT support Django admin, since Django admin has a built-in feature called `autocomplete_fields`. Autocomplete fields are superior and we recommend using them, instead of this package for the admin.

You can find more information here:
https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.ModelAdmin.autocomplete_fields
