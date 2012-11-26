from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name="index.html"), name='home'),
    url(r'^test/', include('testapp.testmain.urls')),
    url(r'^ext/', include('django_select2.urls')),
)
