Extra
=====

Chained select2
---------------

Suppose you have an address form where user should choose a Country and a City.
The problem is different countries have different cities.
So we need to show to the user only cities available in the selected country.

Models
``````

Here are our two models:

.. code-block:: python

    class Country(models.Model):
        name = models.CharField(max_length=255)


    class City(models.Model):
        name = models.CharField(max_length=255)
        country = models.ForeignKey('Country')


Customizing a Form
``````````````````

Lets link two widgets via *country_selector* (it's an arbitrary name for CSS class).

.. code-block:: python
    :emphasize-lines: 7,15,18

    class AddressForm(forms.Form):
        country = forms.ModelChoiceField(
            queryset=Country.objects.all(),
            label=u"Country",
            widget=ModelSelect2Widget(
                search_fields=['name__icontains'],
                attrs={
                    'class': 'country_selector'
                }
            )
        )

        city = forms.ModelChoiceField(
            queryset=City.objects.all(),
            label=u"City",
            widget=ModelSelect2Widget(
                data_url='/cities_by_country/',
                search_fields=['name__icontains'],
                attrs={
                    'data-select2-parents': 'country_selector'
                }
            )
        )


Registering a view
``````````````````

Add new route to *urls.py* for retrieving filtered cities:

.. code-block:: python

    from django.conf.urls import patterns, url
    urlpatterns = patterns(
        # ...
        url('^cities_by_country/$', 'cities_by_country', name='cities_by_country'),
    )

Creating a view
```````````````

Add a method to *views.py*:

.. code-block:: python

    def cities_by_country(request):
        filter_query = Q()
        if request.GET.get('country_selector'):
            filter_query &= Q(country__in=request.GET.getlist('country_selector'))

        result = {
            'results': [
                {
                    'text': instance.name,
                    'id': instance.pk
                } for instance in City.objects.filter(filter_query).distinct().order_by('name')
            ],
            'more': True
        }

        return HttpResponse(json.dumps(result), content_type='application/json')


Interdependent select2
----------------------

Also you may want not to restrict user to which field should be selected first.
Instead you want to suggest to the user options for any select2 depending of his selection in another one.

Customize the form in a manner:

.. code-block:: python
    :emphasize-lines: 5,8-9,17,20-21

    class AddressForm(forms.Form):
        country = forms.ModelChoiceField(
            label=u"Country",
            widget=ModelSelect2Widget(
                data_url='/countries_by_city/',
                search_fields=['name__icontains'],
                attrs={
                    'class': 'country_selector',
                    'data-select2-parents': 'city_selector'
                }
            )
        )

        city = forms.ModelChoiceField(
            label=u"City",
            widget=ModelSelect2Widget(
                data_url='/cities_by_country/',
                search_fields=['name__icontains'],
                attrs={
                    'class': 'city_selector',
                    'data-select2-parents': 'country_selector'
                }
            )
        )


Multi-dependent select2
-----------------------

Furthermore you may want to filter options on two or more select2 selections (some code is dropped for clarity):

.. code-block:: python
    :emphasize-lines: 22

    class SomeForm(forms.Form):
        field1 = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                attrs={
                    'class': 'field1_selector'
                }
            )
        )

        field2 = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                attrs={
                    'class': 'field2_selector'
                }
            )
        )

        field3 = forms.ModelChoiceField(
            widget=ModelSelect2Widget(
                data_url='/field3_by_field1_and_field2/',
                attrs={
                    'data-select2-parents': 'field1_selector field2_selector'
                }
            )
        )

