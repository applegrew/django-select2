from django.conf.urls import patterns, url

urlpatterns = patterns('testapp.testmain.views',
    url(r'single/model/field/$', 'test_single_value_model_field', name='test_single_value_model_field'),
    url(r'single/model/field/([0-9]+)/$', 'test_single_value_model_field1', name='test_single_value_model_field1'),

    url(r'multi/model/field/$', 'test_multi_values_model_field', name='test_multi_values_model_field'),
    url(r'multi/model/field/([0-9]+)/$', 'test_multi_values_model_field1', name='test_multi_values_model_field1'),

    url(r'mixed/form/$', 'test_mixed_form', name='test_mixed_form'),

    url(r'initial/form/$', 'test_init_values', name='test_init_values'),

    url(r'question/$', 'test_list_questions', name='test_list_questions'),
    url(r'question/form/([0-9]+)/$', 'test_tagging', name='test_tagging'),
    url(r'question/form/([0-9]+)/na/$', 'test_tagging_non_auto', name='test_tagging_non_auto'),
    url(r'question/form/$', 'test_tagging_new', name='test_tagging_new'),
    url(r'question/tags/$', 'test_tagging_tags', name='test_tagging_tags'),

    url(r'auto_model/form/$', 'test_auto_multivalue_field', name='test_auto_multivalue_field'),

    url(r'auto_heavy/perf_test/$', 'test_auto_heavy_perf', name='test_auto_heavy_perf'),

    url(r'get_search/get_search_test/$', 'test_get_search_form', name='test_get_search_form'),

    url(r'issue76/$', 'test_issue_73', name='test_issue_73'),
)
