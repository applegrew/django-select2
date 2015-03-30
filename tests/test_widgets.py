# -*- coding:utf-8 -*-
from __future__ import print_function, unicode_literals


class TestWidgets(object):
    url = ""

    def test_is_hidden_multiple(self):
        from django_select2.widgets import HeavySelect2MultipleWidget
        new_widget = HeavySelect2MultipleWidget(data_url="/")
        assert new_widget.is_hidden is False

    def test_is_hidden(self):
        from django_select2.widgets import HeavySelect2Widget
        new_widget = HeavySelect2Widget(data_url="/")
        assert new_widget.is_hidden is False
