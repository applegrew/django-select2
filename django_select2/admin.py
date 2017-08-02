# -*- coding: utf-8 -*-
"""
Django-Select2 Tools for Django Admin.

    Sample usage:
        from django_select2.admin import Select2ModelAdmin
        from django_select2.forms import Select2Widget


        class MyModelAdmin(Select2ModelAdmin):
            select2_fields = {
                'my_choice_field': {
                    'widget': Select2Widget,
                },
                'my_FK_field': {
                    'widget_kwargs': {
                        'search_fields': ['name__icontains'],
                        'attrs': {
                            'data-minimum-input-length': 2,
                            'style': 'width:200px;',
                        },
                    },
                },
            }
"""
from django.conf import settings
from django.contrib import admin
from django.db.models import ForeignKey, ManyToManyField

from .forms import (
    ModelSelect2Mixin, ModelSelect2MultipleWidget, ModelSelect2Widget,
    Select2Widget
)


class Select2ModelAdminMixin(object):
    """
    Base mixin that allows to define and set select2 widgets on model fields.

    It relies on some Django admin.options.BaseModelAdmin attributes and needs
    a single configuration parameter to activate select2 on specific fields.

    ``select_2_fields`` is a dictionary of model field names mapped to a
    configuration dictionary which might be empty, to rely on a fully automatic
    configuration, or containing one or all of the optional settings:
        - ``widget``: user defined widget for that field (e.g. Select2Widget),
          when not provided, the widget is assigned automatically;
        - ``widget_kwargs``: custom arguments for widget initialization
          (e.g. {'search_fields': ['name__icontains']}).

    """

    select2_fields = {}

    def get_widgets(self):
        """Assign select2 widgets as defined via the select2_fields dict."""
        widgets = {}
        for field_name, field_options in self.select2_fields.items():
            user_widget = field_options.get('widget')
            widget_kwargs = field_options.get('widget_kwargs', {})
            db_field = self.model._meta.get_field(field_name)
            field_is_m2m = isinstance(db_field, ManyToManyField)
            field_is_fk = isinstance(db_field, ForeignKey)
            if field_is_fk or field_is_m2m:
                widget = (
                    user_widget or field_is_fk and ModelSelect2Widget or
                    ModelSelect2MultipleWidget
                )
                if issubclass(widget, ModelSelect2Mixin):
                    related_model = (
                        hasattr(db_field, 'remote_field') and
                        db_field.remote_field or db_field.rel
                    ).model
                    # FIXME Change previous line when Django 1.8 is unsupported
                    widget_kwargs['model'] = related_model
                    widget_kwargs.setdefault('attrs', {}).update({
                        'data-related-model': '{}.{}'.format(
                            related_model._meta.app_label,
                            related_model._meta.model_name,
                        ),
                    })
            else:
                widget = user_widget or Select2Widget
                if db_field.choices:
                    widget_kwargs['choices'] = db_field.get_choices(
                        include_blank=db_field.blank,
                        blank_choice=[('', 'None')]
                    )
            widgets[field_name] = widget(**widget_kwargs)
        return widgets

    class Media:
        """Assure the correct js scripts import sequence."""

        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js',
            settings.SELECT2_JS,
            'django_select2/django_select2.js',
            'django_select2/django_select2_formset_handlers.js',
            'django_select2/django_select2_RelatedObjectLookups_fix.js',
        )


class Select2ModelAdmin(Select2ModelAdminMixin, admin.ModelAdmin):
    """Django ModelAdmin supporting select2 on specific model fields."""

    def get_form(self, request, obj=None, **kwargs):
        """Assign select2 widgets to user defined form fields."""
        kwargs.setdefault('widgets', {}).update(self.get_widgets())
        return super(Select2ModelAdmin, self).get_form(request, obj, **kwargs)


class Select2InlineMixin(Select2ModelAdminMixin):
    """The base mixin for Django admin inline configuration classes."""

    def get_formset(self, request, obj=None, **kwargs):
        """Assign select2 widgets to user defined formset form fields."""
        kwargs.setdefault('widgets', {}).update(self.get_widgets())
        return super(Select2InlineMixin, self).get_formset(
            request, obj, **kwargs
        )


class Select2StackedInline(Select2InlineMixin, admin.StackedInline):
    """Django StackedInline supporting select2 on specific fields."""

    pass


class Select2TabularInline(Select2InlineMixin, admin.TabularInline):
    """Django TabularInline supporting select2 on specific fields."""

    pass
