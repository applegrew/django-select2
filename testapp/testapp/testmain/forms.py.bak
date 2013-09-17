from django import forms

from django_select2 import *

from .models import Employee, Dept, ClassRoom, Lab, Word, School, Tag, Question, WordList

from django.core.exceptions import ValidationError

def validate_fail_always(value):
    raise ValidationError(u'%s not valid. Infact nothing is valid!' % value)

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

class MultiWordChoices(AutoModelSelect2MultipleField):
    queryset = Word.objects
    search_fields = ['word__icontains', ]

class TagField(AutoModelSelect2TagField):
    queryset = Tag.objects
    search_fields = ['tag__icontains', ]
    def get_model_field_values(self, value):
        return {'tag': value}

class SelfChoices(AutoSelect2Field):
    def get_val_txt(self, value):
        if not hasattr(self, 'res_map'):
            self.res_map = {}
        return self.res_map.get(value, None)

    def get_results(self, request, term, page, context):
        if not hasattr(self, 'res_map'):
            self.res_map = {}
        mlen = len(self.res_map)
        res = []
        for i in range(1, 6):
            idx = i + mlen
            res.append((idx, term * i,))
            self.res_map[idx] = term * i
        self.choices = res

        return (NO_ERR_RESP, False, res)

class SelfMultiChoices(AutoSelect2MultipleField):
    big_data = {
        1: u"First", 2: u"Second", 3: u"Third",
    }

    def validate_value(self, value):
        if value in [v for v in self.big_data]:
            return True
        else:
            return False

    def coerce_value(self, value):
        return int(value)

    def get_val_txt(self, value):
        if not hasattr(self, '_big_data'):
            self._big_data = dict(self.big_data)
        return self._big_data.get(value, None)

    def get_results(self, request, term, page, context):
        if not hasattr(self, '_big_data'):
            self._big_data = dict(self.big_data)
        res = [(v, self._big_data[v]) for v in self._big_data]
        blen = len(res)
        for i in range(1, 6):
            idx = i + blen
            res.append((idx, term * i,))
            self._big_data[idx] = term * i
        self.choices = res

        return (NO_ERR_RESP, False, res)

########### Forms ##############]

class SchoolForm(forms.ModelForm):
    classes = ClassRoomChoices()

    class Meta:
        model = School

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
                'placeholder': u"Search foo"
            }
        )
    )
    always_fail_rooms = ClassRoomSingleChoices(validators=[validate_fail_always])
    always_fail_rooms_multi = ClassRoomChoices(validators=[validate_fail_always])
    always_fail_self_choice = SelfChoices(validators=[validate_fail_always], auto_id='always_fail_self_choice')
    always_fail_self_choice_multi = SelfMultiChoices(validators=[validate_fail_always], auto_id='always_fail_self_choice_multi')
    model_with_both_required_and_empty_label_false = ModelSelect2Field(
        queryset=Employee.objects, empty_label=None, required=False) #issue#26

# These are just for testing Auto registration of fields
EmployeeChoices() # Should already be registered
EmployeeChoices(auto_id="EmployeeChoices_CustomAutoId") # Should get registered

class InitialValueForm(forms.Form):
    select2Choice = Select2ChoiceField(initial=2,
        choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    select2MultipleChoice = Select2MultipleChoiceField(initial=[2,3],
        choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    heavySelect2Choice = AutoSelect2Field(initial=2,
        choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    heavySelect2MultipleChoice = AutoSelect2MultipleField(initial=[1,3],
        choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    self_choices = SelfChoices(label='Self copy choices', initial=2,
        choices=((1, "First"), (2, "Second"), (3, "Third"), ))
    self_multi_choices = SelfMultiChoices(label='Self copy multi-choices', initial=[2,3])
    select2ChoiceWithQuotes = Select2ChoiceField(initial=2,
        choices=((1, "'Single-Quote'"), (2, "\"Double-Quotes\""), (3, "\"Mixed-Quotes'"), ))
    heavySelect2ChoiceWithQuotes = AutoSelect2Field(initial=2,
        choices=((1, "'Single-Quote'"), (2, "\"Double-Quotes\""), (3, "\"Mixed-Quotes'"), ))

class QuestionForm(forms.ModelForm):
    question = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
    tags = TagField()

    class Meta:
        model = Question

class WordsForm(forms.ModelForm):
    word = WordChoices()
    words = MultiWordChoices()

    class Meta:
        model = WordList
        exclude = ['kind']
