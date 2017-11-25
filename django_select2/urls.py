"""
Django-Select2 URL configuration.

Add `django_select` to your ``urlconf`` **if** you use any 'Model' fields::

    url(r'^select2/', include('django_select2.urls')),

"""
from django.conf.urls import url

from .views import AutoResponseView

urlpatterns = [
    url(r"^fields/auto.json$",
        AutoResponseView.as_view(), name="django_select2-json"),
]
