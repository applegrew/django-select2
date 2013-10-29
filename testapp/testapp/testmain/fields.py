from django_select2 import AutoSelect2MultipleField, AutoModelSelect2MultipleField
from django_select2 import NO_ERR_RESP

from .models import Dept

class GetSearchTestField(AutoSelect2MultipleField):
    """
    Selects an employee.
    This field does not render the form value on search results presentation.
    """
    def security_check(self, request, *args, **kwargs):
        return True
    def get_results(self, request, term, page, context):
        """
        Just a trivial example, with fixed values.
        """
        res = [('Green Gold','Green Gold'),('Hulk','Hulk'),]
        return (NO_ERR_RESP, False, res)

    def get_val_txt(self, value):
        """
        The problem of issue #66 was here. I was not overriding this.
        When using AutoSelect2MultipleField you should implement get_val_txt in this case.
        I think that this is because there should be an unique correspondence between
        the referenced value and the shown value
        In this particular example, the referenced value and the shown value are the same
        """
        return unicode(value)

class GetModelSearchTestField(AutoModelSelect2MultipleField):
    """
    Selects a department.
    This field does render the form value on search results presentation. Works OK.
    """
    queryset = Dept.objects.all()
    search_fields = ['name__icontains']
    to_field = 'name'

    def security_check(self, request, *args, **kwargs):
        return True