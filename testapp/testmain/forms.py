from django import forms

from django_select2 import *

from .models import Employee, Dept, ClassRoom

class EmployeeChoices(AutoModelSelect2Field):
    queryset = Employee.objects
    search_fields = ['name__icontains', ]

class EmployeeForm(forms.ModelForm):
    manager = EmployeeChoices()
    dept = ModelSelect2Field(queryset=Dept.objects)
    
    class Meta:
        model = Employee

#class DeptForm(forms.ModelForm):
#    allotted_rooms = ModelMultipleSelect2Field(queryset=ClassRoom.objects)

#    class Meta:
#        model = Dept