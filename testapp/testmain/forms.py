from django import forms

from django_select2 import *

from .models import Employee, Dept, ClassRoom, Lab

class EmployeeChoices(AutoModelSelect2Field):
    queryset = Employee.objects
    search_fields = ['name__icontains', ]

class ClassRoomChoices(AutoModelSelect2MultipleField):
    queryset = ClassRoom.objects
    search_fields = ['number__icontains', ]


class EmployeeForm(forms.ModelForm):
    manager = EmployeeChoices(required=False)
    dept = ModelSelect2Field(queryset=Dept.objects)
    
    class Meta:
        model = Employee

class DeptForm(forms.ModelForm):
    allotted_rooms = ClassRoomChoices()
    allotted_labs = ModelSelect2MultipleField(queryset=Lab.objects, required=False)

    class Meta:
        model = Dept

# These are just for testing Auto registration of fields
EmployeeChoices() # Should already be registered
EmployeeChoices(auto_id="EmployeeChoices_CustomAutoId") # Should get registered
