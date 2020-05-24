"""
Django-Select2 Widgets.

These components are responsible for rendering
the necessary HTML data markups. Since this whole
package is to render choices using Select2 JavaScript
library, hence these components are meant to be used
with choice fields.

Widgets are generally of two types:

    1. **Light** --
    They are not meant to be used when there
    are too many options, say, in thousands.
    This is because all those options would
    have to be pre-rendered onto the page
    and JavaScript would be used to search
    through them. Said that, they are also one
    the most easiest to use. They are a
    drop-in-replacement for Django's default
    select widgets.

    2(a). **Heavy** --
    They are suited for scenarios when the number of options
    are large and need complex queries (from maybe different
    sources) to get the options.

    This dynamic fetching of options undoubtedly requires
    Ajax communication with the server. Django-Select2 includes
    a helper JS file which is included automatically,
    so you need not worry about writing any Ajax related JS code.
    Although on the server side you do need to create a view
    specifically to respond to the queries.

    2(b). **Model** --
    Model-widgets are a further specialized versions of Heavies.
    These do not require views to serve Ajax requests.
    When they are instantiated, they register themselves
    with one central view which handles Ajax requests for them.

Heavy and Model widgets have respectively the word 'Heavy' and 'Model' in
their name.  Light widgets are normally named, i.e. there is no 'Light' word
in their names.

.. inheritance-diagram:: django_select2.forms
    :parts: 1

"""
import uuid
from functools import reduce
from itertools import chain
from pickle import PicklingError  # nosec

from django import forms
from django.contrib.admin.widgets import SELECT2_TRANSLATIONS
from django.core import signing
from django.db.models import Q
from django.forms.models import ModelChoiceIterator
from django.urls import reverse
from django.utils.translation import get_language

from .cache import cache
from .conf import settings


class Select2Mixin:
    """
    The base mixin of all Select2 widgets.

    This mixin is responsible for rendering the necessary
    data attributes for select2 as well as adding the static
    form media.
    """

    empty_label = ""

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add select2 data attributes."""
        default_attrs = {"data-minimum-input-length": 0}
        if self.is_required:
            default_attrs["data-allow-clear"] = "false"
        else:
            default_attrs["data-allow-clear"] = "true"
            default_attrs["data-placeholder"] = self.empty_label or ""

        default_attrs.update(base_attrs)
        attrs = super().build_attrs(default_attrs, extra_attrs=extra_attrs)

        if "class" in attrs:
            attrs["class"] += " django-select2"
        else:
            attrs["class"] = "django-select2"
        return attrs

    def optgroups(self, name, value, attrs=None):
        """Add empty option for clearable selects."""
        if not self.is_required and not self.allow_multiple_selected:
            self.choices = list(chain([("", "")], self.choices))
        return super().optgroups(name, value, attrs=attrs)

    def _get_media(self):
        """
        Construct Media as a dynamic property.

        .. Note:: For more information visit
            https://docs.djangoproject.com/en/stable/topics/forms/media/#media-as-a-dynamic-property
        """
        lang = get_language()
        select2_js = (settings.SELECT2_JS,) if settings.SELECT2_JS else ()
        select2_css = (settings.SELECT2_CSS,) if settings.SELECT2_CSS else ()

        i18n_name = SELECT2_TRANSLATIONS.get(lang)
        if i18n_name not in settings.SELECT2_I18N_AVAILABLE_LANGUAGES:
            i18n_name = None

        i18n_file = (
            ("%s/%s.js" % (settings.SELECT2_I18N_PATH, i18n_name),) if i18n_name else ()
        )

        return forms.Media(
            js=select2_js + i18n_file + ("django_select2/django_select2.js",),
            css={"screen": select2_css},
        )

    media = property(_get_media)


class Select2TagMixin:
    """Mixin to add select2 tag functionality."""

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add select2's tag attributes."""
        default_attrs = {
            "data-minimum-input-length": 1,
            "data-tags": "true",
            "data-token-separators": '[",", " "]',
        }
        default_attrs.update(base_attrs)
        return super().build_attrs(default_attrs, extra_attrs=extra_attrs)


class Select2Widget(Select2Mixin, forms.Select):
    """
    Select2 drop in widget.

    Example usage::

        class MyModelForm(forms.ModelForm):
            class Meta:
                model = MyModel
                fields = ('my_field', )
                widgets = {
                    'my_field': Select2Widget
                }

    or::

        class MyForm(forms.Form):
            my_choice = forms.ChoiceField(widget=Select2Widget)

    """


class Select2MultipleWidget(Select2Mixin, forms.SelectMultiple):
    """
    Select2 drop in widget for multiple select.

    Works just like :class:`.Select2Widget` but for multi select.
    """


class Select2TagWidget(Select2TagMixin, Select2Mixin, forms.SelectMultiple):
    """
    Select2 drop in widget for for tagging.

    Example for :class:`.django.contrib.postgres.fields.ArrayField`::

        class MyWidget(Select2TagWidget):

            def value_from_datadict(self, data, files, name):
                values = super().value_from_datadict(data, files, name):
                return ",".join(values)

            def optgroups(self, name, value, attrs=None):
                values = value[0].split(',') if value[0] else []
                selected = set(values)
                subgroup = [self.create_option(name, v, v, selected, i) for i, v in enumerate(values)]
                return [(None, subgroup, 0)]

    """


class HeavySelect2Mixin:
    """Mixin that adds select2's AJAX options and registers itself on Django's cache."""

    dependent_fields = {}

    def __init__(self, attrs=None, choices=(), **kwargs):
        """
        Return HeavySelect2Mixin.

        Args:
            data_view (str): URL pattern name
            data_url (str): URL
            dependent_fields (dict): Dictionary of dependent parent fields.
                The value of the dependent field will be passed as to :func:`.filter_queryset`.
                It can be used to further restrict the search results. For example, a city
                widget could be dependent on a country.
                Key is a name of a field in a form.
                Value is a name of a field in a model (used in `queryset`).

        """
        self.choices = choices
        if attrs is not None:
            self.attrs = attrs.copy()
        else:
            self.attrs = {}

        self.uuid = str(uuid.uuid4())
        self.field_id = signing.dumps(self.uuid)
        self.data_view = kwargs.pop("data_view", None)
        self.data_url = kwargs.pop("data_url", None)

        dependent_fields = kwargs.pop("dependent_fields", None)
        if dependent_fields is not None:
            self.dependent_fields = dict(dependent_fields)
        if not (self.data_view or self.data_url):
            raise ValueError('You must ether specify "data_view" or "data_url".')
        self.userGetValTextFuncName = kwargs.pop("userGetValTextFuncName", "null")

    def get_url(self):
        """Return URL from instance or by reversing :attr:`.data_view`."""
        if self.data_url:
            return self.data_url
        return reverse(self.data_view)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Set select2's AJAX attributes."""
        default_attrs = {
            "data-ajax--url": self.get_url(),
            "data-ajax--cache": "true",
            "data-ajax--type": "GET",
            "data-minimum-input-length": 2,
        }

        if self.dependent_fields:
            default_attrs["data-select2-dependent-fields"] = " ".join(
                self.dependent_fields
            )

        default_attrs.update(base_attrs)

        attrs = super().build_attrs(default_attrs, extra_attrs=extra_attrs)

        attrs["data-field_id"] = self.field_id

        attrs["class"] += " django-select2-heavy"
        return attrs

    def render(self, *args, **kwargs):
        """Render widget and register it in Django's cache."""
        output = super().render(*args, **kwargs)
        self.set_to_cache()
        return output

    def _get_cache_key(self):
        return "%s%s" % (settings.SELECT2_CACHE_PREFIX, self.uuid)

    def set_to_cache(self):
        """
        Add widget object to Django's cache.

        You may need to overwrite this method, to pickle all information
        that is required to serve your JSON response view.
        """
        try:
            cache.set(self._get_cache_key(), {"widget": self, "url": self.get_url()})
        except (PicklingError, AttributeError):
            msg = 'You need to overwrite "set_to_cache" or ensure that %s is serialisable.'
            raise NotImplementedError(msg % self.__class__.__name__)


class HeavySelect2Widget(HeavySelect2Mixin, Select2Widget):
    """
    Select2 widget with AJAX support that registers itself to Django's Cache.

    Usage example::

        class MyWidget(HeavySelect2Widget):
            data_view = 'my_view_name'

    or::

        class MyForm(forms.Form):
            my_field = forms.ChoiceField(
                widget=HeavySelect2Widget(
                    data_url='/url/to/json/response'
                )
            )

    """


class HeavySelect2MultipleWidget(HeavySelect2Mixin, Select2MultipleWidget):
    """Select2 multi select widget similar to :class:`.HeavySelect2Widget`."""


class HeavySelect2TagWidget(HeavySelect2Mixin, Select2TagWidget):
    """Select2 tag widget."""


# Auto Heavy widgets


class ModelSelect2Mixin:
    """Widget mixin that provides attributes and methods for :class:`.AutoResponseView`."""

    model = None
    queryset = None
    search_fields = []
    """
    Model lookups that are used to filter the QuerySet.

    Example::

        search_fields = [
                'title__icontains',
            ]

    """

    max_results = 25
    """Maximal results returned by :class:`.AutoResponseView`."""

    @property
    def empty_label(self):
        if isinstance(self.choices, ModelChoiceIterator):
            return self.choices.field.empty_label
        return ""

    def __init__(self, *args, **kwargs):
        """
        Overwrite class parameters if passed as keyword arguments.

        Args:
            model (django.db.models.Model): Model to select choices from.
            queryset (django.db.models.query.QuerySet): QuerySet to select choices from.
            search_fields (list): List of model lookup strings.
            max_results (int): Max. JsonResponse view page size.

        """
        self.model = kwargs.pop("model", self.model)
        self.queryset = kwargs.pop("queryset", self.queryset)
        self.search_fields = kwargs.pop("search_fields", self.search_fields)
        self.max_results = kwargs.pop("max_results", self.max_results)
        defaults = {"data_view": "django_select2:auto-json"}
        defaults.update(kwargs)
        super().__init__(*args, **defaults)

    def set_to_cache(self):
        """
        Add widget's attributes to Django's cache.

        Split the QuerySet, to not pickle the result set.
        """
        queryset = self.get_queryset()
        cache.set(
            self._get_cache_key(),
            {
                "queryset": [queryset.none(), queryset.query],
                "cls": self.__class__,
                "search_fields": tuple(self.search_fields),
                "max_results": int(self.max_results),
                "url": str(self.get_url()),
                "dependent_fields": dict(self.dependent_fields),
            },
        )

    def filter_queryset(self, request, term, queryset=None, **dependent_fields):
        """
        Return QuerySet filtered by search_fields matching the passed term.

        Args:
            request (django.http.request.HttpRequest): The request is being passed from
                the JSON view and can be used to dynamically alter the response queryset.
            term (str): Search term
            queryset (django.db.models.query.QuerySet): QuerySet to select choices from.
            **dependent_fields: Dependent fields and their values. If you want to inherit
                from ModelSelect2Mixin and later call to this method, be sure to pop
                everything from keyword arguments that is not a dependent field.

        Returns:
            QuerySet: Filtered QuerySet

        """
        if queryset is None:
            queryset = self.get_queryset()
        search_fields = self.get_search_fields()
        select = Q()
        term = term.replace("\t", " ")
        term = term.replace("\n", " ")
        for t in [t for t in term.split(" ") if not t == ""]:
            select &= reduce(
                lambda x, y: x | Q(**{y: t}),
                search_fields[1:],
                Q(**{search_fields[0]: t}),
            )
        if dependent_fields:
            select &= Q(**dependent_fields)

        return queryset.filter(select).distinct()

    def get_queryset(self):
        """
        Return QuerySet based on :attr:`.queryset` or :attr:`.model`.

        Returns:
            QuerySet: QuerySet of available choices.

        """
        if self.queryset is not None:
            queryset = self.queryset
        elif hasattr(self.choices, "queryset"):
            queryset = self.choices.queryset
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise NotImplementedError(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
            )
        return queryset

    def get_search_fields(self):
        """Return list of lookup names."""
        if self.search_fields:
            return self.search_fields
        raise NotImplementedError(
            '%s, must implement "search_fields".' % self.__class__.__name__
        )

    def optgroups(self, name, value, attrs=None):
        """Return only selected options and set QuerySet from `ModelChoicesIterator`."""
        default = (None, [], 0)
        groups = [default]
        has_selected = False
        selected_choices = {str(v) for v in value}
        if not self.is_required and not self.allow_multiple_selected:
            default[1].append(self.create_option(name, "", "", False, 0))
        if not isinstance(self.choices, ModelChoiceIterator):
            return super().optgroups(name, value, attrs=attrs)
        selected_choices = {
            c for c in selected_choices if c not in self.choices.field.empty_values
        }
        field_name = self.choices.field.to_field_name or "pk"
        query = Q(**{"%s__in" % field_name: selected_choices})
        for obj in self.choices.queryset.filter(query):
            option_value = self.choices.choice(obj)[0]
            option_label = self.label_from_instance(obj)

            selected = str(option_value) in value and (
                has_selected is False or self.allow_multiple_selected
            )
            if selected is True and has_selected is False:
                has_selected = True
            index = len(default[1])
            subgroup = default[1]
            subgroup.append(
                self.create_option(
                    name, option_value, option_label, selected_choices, index
                )
            )
        return groups

    def label_from_instance(self, obj):
        """
        Return option label representation from instance.

        Can be overridden to change the representation of each choice.

        Example usage::

            class MyWidget(ModelSelect2Widget):
                def label_from_instance(obj):
                    return str(obj.title).upper()

        Args:
            obj (django.db.models.Model): Instance of Django Model.

        Returns:
            str: Option label.

        """
        return str(obj)


class ModelSelect2Widget(ModelSelect2Mixin, HeavySelect2Widget):
    """
    Select2 drop in model select widget.

    Example usage::

        class MyWidget(ModelSelect2Widget):
            search_fields = [
                'title__icontains',
            ]

        class MyModelForm(forms.ModelForm):
            class Meta:
                model = MyModel
                fields = ('my_field', )
                widgets = {
                    'my_field': MyWidget,
                }

    or::

        class MyForm(forms.Form):
            my_choice = forms.ChoiceField(
                widget=ModelSelect2Widget(
                    model=MyOtherModel,
                    search_fields=['title__icontains']
                )
            )

    .. tip:: The ModelSelect2(Multiple)Widget will try
        to get the QuerySet from the fields choices.
        Therefore you don't need to define a QuerySet,
        if you just drop in the widget for a ForeignKey field.
    """


class ModelSelect2MultipleWidget(ModelSelect2Mixin, HeavySelect2MultipleWidget):
    """
    Select2 drop in model multiple select widget.

    Works just like :class:`.ModelSelect2Widget` but for multi select.
    """


class ModelSelect2TagWidget(ModelSelect2Mixin, HeavySelect2TagWidget):
    """
    Select2 model widget with tag support.

    This it not a simple drop in widget.
    It requires to implement you own :func:`.value_from_datadict`
    that adds missing tags to you QuerySet.

    Example::

        class MyModelSelect2TagWidget(ModelSelect2TagWidget):
            queryset = MyModel.objects.all()

            def value_from_datadict(self, data, files, name):
                '''Create objects for given non-pimary-key values. Return list of all primary keys.'''
                values = set(super().value_from_datadict(data, files, name))
                # This may only work for MyModel, if MyModel has title field.
                # You need to implement this method yourself, to ensure proper object creation.
                pks = self.queryset.filter(**{'pk__in': list(values)}).values_list('pk', flat=True)
                pks = set(map(str, pks))
                cleaned_values = list(values)
                for val in values - pks:
                    cleaned_values.append(self.queryset.create(title=val).pk)
                return cleaned_values

    """
