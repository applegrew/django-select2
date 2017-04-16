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
                search_fields=['name__icontains'],
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

