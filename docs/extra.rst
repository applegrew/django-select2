Extra
=====

Chained select2
---------------

Suppose you have an address form where a user should choose a Country and a City.
When the user selects a country we want to show only cities belonging to that country.
So the one selector depends on another one.

Models
``````

Here are our two models:

.. code-block:: python

    class Country(models.Model):
        name = models.CharField(max_length=255)


    class City(models.Model):
        name = models.CharField(max_length=255)
        country = models.ForeignKey('Country', related_name="cities")


Customizing a Form
``````````````````

Lets link two widgets via *dependent_fields*.

.. code-block:: python
    :emphasize-lines: 15

    class AddressForm(forms.Form):
        country = forms.ModelChoiceField(
            queryset=Country.objects.all(),
            label=u"Country",
            widget=ModelSelect2Widget(
                model=Country,
                search_fields=['name__icontains'],
            )
        )

        city = forms.ModelChoiceField(
            queryset=City.objects.all(),
            label=u"City",
            widget=ModelSelect2Widget(
                model=City,
                search_fields=['name__icontains'],
                dependent_fields={'country': 'country'},
                max_results=500,
            )
        )


Interdependent select2
----------------------

Also you may want not to restrict the user to which field should be selected first.
Instead you want to suggest to the user options for any select2 depending of his selection in another one.

Customize the form in a manner:

.. code-block:: python
    :emphasize-lines: 7

    class AddressForm(forms.Form):
        country = forms.ModelChoiceField(
            queryset=Country.objects.all(),
            label=u"Country",
            widget=ModelSelect2Widget(
                search_fields=['name__icontains'],
                dependent_fields={'city': 'cities'},
            )
        )

        city = forms.ModelChoiceField(
            queryset=City.objects.all(),
            label=u"City",
            widget=ModelSelect2Widget(
                search_fields=['name__icontains'],
                dependent_fields={'country': 'country'},
                max_results=500,
            )
        )

Take attention to country's dependent_fields. The value of 'city' is 'cities' because of
related name used in a filter condition `cities` which differs from widget field name `city`.

.. caution::
    Be aware of using interdependent select2 in parent-child relation.
    When a child is selected, you are restricted to change parent (only one value is available).
    Probably you should let the user reset the child first to release parent select2.


Multi-dependent select2
-----------------------

Furthermore you may want to filter options on two or more select2 selections (some code is dropped for clarity):

.. code-block:: python
    :emphasize-lines: 14

    class SomeForm(forms.Form):
        field1 = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
            )
        )

        field2 = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
            )
        )

        field3 = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                dependent_fields={'field1': 'field1', 'field2': 'field2'},
            )
        )


GenericForeignKey select2
---------------------------
There is some requirements to use django select2 for GenericForeignKey


Models
``````
Suppose we have a Model Article that has GenericForeignKey relation

.. code-block:: python

    class Article(MediaMixin, models.Model):
    ...
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to=(
            models.Q(app_label='users', model='user'),
            ...
        ),
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        'content_type',
        'object_id'
    )




You need to add list called SELECT2_SEARCH_FIELDS to all models that can be selected as Content type

.. code-block:: python
    :emphasize-lines: 3

    class User(models.Model):
        ...
        SELECT2_SEARCH_FIELDS=['email__icontains']



Form
``````

In the form you must make dependent_fields={'content_type': 'content_type_gfk'},
The value `content_type_gfk` will make django-select2 able to understand that this field is GenericForeignKey

.. code-block:: python
    :emphasize-lines: 6

    class ArticleForm(forms.ModelForm):
        object_id = forms.ModelChoiceField(
            queryset=ContentType.objects.none(),
            label=u"Related Position",
            widget=ModelSelect2Widget(
                dependent_fields={'content_type': 'content_type_gfk'},
                max_results=20,
                attrs={'data-placeholder': 'Search for related position object', 'data-width': '30em'},
            )
        )


Admin
``````

Example using GFK in admin

.. code-block:: python

    class ArticleAdmin(admin.ModelAdmin):
        form = ArticleForm

    admin.site.register(Article, ArticleAdmin)
