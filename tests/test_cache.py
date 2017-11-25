def test_default_cache():
    from django_select2.cache import cache

    cache.set('key', 'value')

    assert cache.get('key') == 'value'
