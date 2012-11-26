from django.conf.urls import patterns, url

urlpatterns = patterns('testapp.testmain.views',
    url(r'single/model/field/$', 'test_single_value_model_field', name='test_single_value_model_field'),
    url(r'single/model/field/([0-9]+)/$', 'test_single_value_model_field1', name='test_single_value_model_field1'),

    url(r'multi/model/field/$', 'test_multi_values_model_field', name='test_multi_values_model_field'),
    url(r'multi/model/field/([0-9]+)/$', 'test_multi_values_model_field1', name='test_multi_values_model_field1'),

    url(r'mixed/form/$', 'test_mixed_form', name='test_mixed_form'),

    url(r'initial/form/$', 'test_init_values', name='test_init_values'),
)
