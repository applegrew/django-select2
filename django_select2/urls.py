"""
Django-Select2 URL configuration.

Add `django_select` to your ``urlconf`` **if** you use any 'Model' fields::

    from django.urls import path


    path('select2/', include('django_select2.urls')),

"""
from django.urls import path

from .views import AutoResponseView

app_name = 'django_select2'

urlpatterns = [
    path("fields/auto.json", AutoResponseView.as_view(), name="auto-json"),
]
