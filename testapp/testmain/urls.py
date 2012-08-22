from django.conf.urls.defaults import *

urlpatterns = patterns("",
	url(r'single/model/field/$', 'testmain.views.test_single_value_model_field', name='test_single_value_model_field'),
    url(r'single/model/field/([0-9]+)/$', 'testmain.views.test_single_value_model_field1', name='test_single_value_model_field1'),

    url(r'multi/model/field/$', 'testmain.views.test_multi_values_model_field', name='test_multi_values_model_field'),
    url(r'multi/model/field/([0-9]+)/$', 'testmain.views.test_multi_values_model_field1', name='test_multi_values_model_field1'),

    url(r'mixed/form/$', 'testmain.views.test_mixed_form', name='test_mixed_form'),
)
