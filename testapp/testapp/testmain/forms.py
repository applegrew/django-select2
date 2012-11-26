from django import forms

from django_select2 import *

from .models import Employee, Dept, ClassRoom, Lab, Word

############# Choice fields ###################

class EmployeeChoices(AutoModelSelect2Field):
    queryset = Employee.objects
    search_fields = ['name__icontains', ]

class ClassRoomChoices(AutoModelSelect2MultipleField):
    queryset = ClassRoom.objects
    search_fields = ['number__icontains', ]

class ClassRoomSingleChoices(AutoModelSelect2Field):
    queryset = ClassRoom.objects
    search_fields = ['number__icontains', ]

class WordChoices(AutoModelSelect2Field):
    queryset = Word.objects
    search_fields = ['word__icontains', ]

class SelfChoices(AutoSelect2Field):
    def get_results(self, request, term, page, context):
        res = []
        for i in range(1, 6):
            res.append((i, term * i,))
        self.choices = res

        return (NO_ERR_RESP, False, res)

class SelfMultiChoices(AutoSelect2MultipleField):
    big_data = {
        1: "First", 2: "Second", 3: "Third",
        }

    def validate_value(self, value):
        if value in [v for v in self.big_data]:
            return True
        else:
            return False

    def coerce_value(self, value):
        return int(value)

    def get_val_txt(self, value):
        return self.big_data.get(value, None)

    def get_results(self, request, term, page, context):
        res = [(v, self.big_data[v]) for v in self.big_data]
        for i in range(len(res), 6):
            res.append((i, term * i,))

        return (NO_ERR_RESP, False, res)

########### Forms ##############

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

class MixedForm(forms.Form):
    emp1 = EmployeeChoices()
    rooms1 = ClassRoomChoices()
    emp2 = EmployeeChoices()
    rooms2 = ClassRoomChoices()
    rooms3 = ClassRoomSingleChoices()
    any_word = WordChoices()
    self_choices = SelfChoices(label='Self copy choices')
    self_multi_choices = SelfMultiChoices(label='Self copy multi-choices')
    issue11_test = EmployeeChoices(
        label='Issue 11 Test (Employee)',
        widget=AutoHeavySelect2Widget(
            select2_options={
                'width': '32em',
                'placeHolder': u"Search foo"
            }
        )
    )

# These are just for testing Auto registration of fields
EmployeeChoices() # Should already be registered
EmployeeChoices(auto_id="EmployeeChoices_CustomAutoId") # Should get registered

class InitialValueForm(forms.Form):
    select2Choice = Select2ChoiceField(initial=2, choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    select2MultipleChoice = Select2MultipleChoiceField(initial=[2,3], choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    heavySelect2Choice = AutoSelect2Field(initial=2, choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    heavySelect2MultipleChoice = AutoSelect2MultipleField(initial=[1,3], choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    self_choices = SelfChoices(label='Self copy choices', initial=2, choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    self_multi_choices = SelfMultiChoices(label='Self copy multi-choices', initial=[2,3])

