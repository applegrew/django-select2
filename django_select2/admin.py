"""
Django-Select2 Tools for Django Admin.

The base usage is simply inheriting from the provided mixin when
declaring admin classes and declaring.

    Ex.
        from django.contrib.admin import ModelAdmin
        from django_select2.admin import Select2AdminMixin
        from django_select2.forms import Select2Widget


        class MyModelAdmin(Select2AdminMixin, ModelAdmin):
            select2_fields = {
                'my_first_field': {
                    'widget': Select2Widget,
                },
                'my_second_field': {
                    'widget_kwargs': {
                        'search_fields': ['name__icontains'],
                    },
                },
            }

"""
from django.contrib import admin
from django.db.models import ForeignKey, ManyToManyField
from django.forms.models import ModelForm, ModelFormMetaclass

from .forms import (ModelSelect2Mixin, ModelSelect2MultipleWidget,
                    ModelSelect2Widget, Select2Widget)


class Select2AdminMixin(object):
    """
    The base mixin for Django admin configuration classes.

    This mixin is responsible for making sure that the widget media are
    correctly collected while providing integration with the Django wrapper
    that renders the visual tools to interact with related models (i.e. the
    add, edit and delete buttons next to the widget in the admin).

    The user should inherit first from this mixin and then from the intended
    Django admin options class (e.g. ModelAdmin). Then, in order to activate
    the select2 widget on specific fields, the user must define a class
    attribute "select_2_fields" as a dict containing the intended fields
    names as keys and a dict containing options as values.
    In the simplest case, the options dict can be empty, because the
    intended behaviour is automatically inferred from the model field type.
    However two other functionalities are available:
    - using the 'widget' key, the user can provide a custom widget class,
    - using the 'widget_kwargs' key, the user can provide the arguments for
      the widget initialisation. When used alone, this relies on the default
      widgets automatically chosen according to the field type.
    - using the 'permissions' key, the user can provide a custom dict of
      boolean permissions:
        e.g. {'can_add': True, 'can_change': True, 'can_delete': False}
      for the related model admin wrapper. If explicitly set to an empty dict,
      disables the related model admin wrapper, while missing or missing keys
      default to the user permissions on the related model.
    """
    select2_fields = {}

    def get_form(self, request, obj=None, **kwargs):

        def get_formfield(field_name):
            field_options = self.select2_fields.get(field_name, {}).copy()
            widget_kwargs = field_options.get('widget_kwargs', {})
            widget_kwargs.setdefault('attrs', {}).setdefault(
                'style', 'width:300px')
            db_field = self.model._meta.get_field(field_name)
            field_is_m2m = isinstance(db_field, ManyToManyField)
            field_is_fk = isinstance(db_field, ForeignKey)
            user_widget = field_options.get('widget')
            formfield = db_field.formfield()
            if field_is_fk or field_is_m2m:
                widget = (
                    user_widget or field_is_fk and ModelSelect2Widget or
                    ModelSelect2MultipleWidget)
                if issubclass(widget, ModelSelect2Mixin):
                    widget_kwargs['model'] = db_field.remote_field.model
                widget_kwargs['attrs'].setdefault(
                    'data-minimum-input-length', 5)
                related_modeladmin = self.admin_site._registry.get(
                    db_field.remote_field.model)
                wrapper_kwargs = {}
                default_permissions = {
                    'can_add': (
                        related_modeladmin and
                        related_modeladmin.has_add_permission(request)),
                    'can_change': (
                        related_modeladmin and
                        related_modeladmin.has_change_permission(request)),
                    'can_delete': (
                        related_modeladmin and
                        related_modeladmin.has_delete_permission(request)),
                }
                custom_permissions = field_options.get(
                    'permissions', default_permissions)
                if custom_permissions:
                    wrapper_kwargs.update(
                        can_add_related=(
                            default_permissions['can_add'] and
                            custom_permissions.get('can_add', False)),
                        can_change_related=(
                            default_permissions['can_change'] and
                            custom_permissions.get('can_change', False)),
                        can_delete_related=(
                            default_permissions['can_delete'] and
                            custom_permissions.get('can_delete', False)),
                    )
                    formfield.widget = admin.widgets.RelatedFieldWidgetWrapper(
                        widget(**widget_kwargs), db_field.remote_field,
                        self.admin_site, **wrapper_kwargs)
                else:
                    formfield.widget = widget(**widget_kwargs)
            elif db_field.choices:
                widget = user_widget or Select2Widget
                widget_kwargs['choices'] = db_field.get_choices(
                    include_blank=db_field.blank,
                    blank_choice=[('', 'None')]
                )
                formfield.widget = widget(**widget_kwargs)
            else:
                widget = user_widget or Select2Widget
                formfield.widget = widget(**widget_kwargs)
            return formfield

        class CustomFormMetaclass(ModelFormMetaclass):
            def __new__(mcs, name, bases, attrs):
                for field_name in self.select2_fields:
                    formfield = get_formfield(field_name)
                    formfield and attrs.setdefault(field_name, formfield)
                return super(CustomFormMetaclass, mcs).__new__(
                    mcs, name, bases, attrs)

        if isinstance(self, admin.ModelAdmin):
            form_class = super(Select2AdminMixin, self).get_form(
                request, obj, **kwargs)
        elif isinstance(self, admin.options.InlineModelAdmin):
            form_class = self.form
        else:
            form_class = ModelForm

        class CustomForm(form_class, metaclass=CustomFormMetaclass):
            pass

        return CustomForm

    class Media:
        js = ['https://code.jquery.com/jquery-2.2.4.min.js']


class Select2AdminInlineMixin(Select2AdminMixin):
    """
    The base mixin for Django admin inline configuration classes.

    This mixin is responsible for making sure that the widget media are
    correctly collected while providing integration with the Django wrapper
    that renders the visual tools to interact with related models (i.e. the
    add, edit and delete buttons next to the widget in the admin).

    The user should inherit first from this mixin and then from the intended
    Django admin options class (e.g. ModelAdmin). Then, in order to activate
    the select2 widget on specific fields, the user must define a class
    attribute "select_2_fields" as a dict containing the intended fields
    names as keys and a dict containing options as values.
    In the simplest case, the options dict can be empty, because the
    intended behaviour is automatically inferred from the model field type.
    However two other functionalities are available:
    - using the 'widget' key, the user can provide a custom widget,
    - using the 'widget_kwargs' key, the user can provide the arguments for
      the widget initialisation. When used alone, this relies on the default
      widgets automatically chosen according to the field type.
    """
    def get_formset(self, request, obj=None, **kwargs):
        kwargs['form'] = self.get_form(request, obj)
        return super(Select2AdminInlineMixin, self).get_formset(
            request, obj, **kwargs)

    class Media:
        js = ['https://code.jquery.com/jquery-2.2.4.min.js']
