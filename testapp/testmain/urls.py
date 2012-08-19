from django.conf.urls.defaults import *

urlpatterns = patterns("",
	url(r'auto/model/field/$', 'testmain.views.test_auto_model_field', name='test_auto_model_field'),
    url(r'auto/model/field/([0-9]+)/$', 'testmain.views.test_auto_model_field1', name='test_auto_model_field2'),
)
