import json
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404

from .forms import EmployeeForm, DeptForm, MixedForm, InitialValueForm, QuestionForm, QuestionNonAutoForm, WordsForm, SchoolForm, \
    GetSearchTestForm, AnotherWordForm
from .models import Employee, Dept, Question, WordList, School, Tag

def test_single_value_model_field(request):
    return render(request, 'list.html', {
    	'title': 'Employees',
    	'href': 'test_single_value_model_field1',
    	'object_list': Employee.objects.all(),
        'create_new_href': ''
	})

def test_single_value_model_field1(request, id):
    emp =  get_object_or_404(Employee, pk=id)
    if request.POST:
        form = EmployeeForm(data=request.POST, instance=emp)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = EmployeeForm(instance=emp)
    return render(request, 'form.html', {'form': form})


def test_multi_values_model_field(request):
    return render(request, 'list.html', {
    	'title': 'Departments',
    	'href': 'test_multi_values_model_field1',
    	'object_list': Dept.objects.all(),
        'create_new_href': ''
	})  

def test_multi_values_model_field1(request, id):
    dept =  get_object_or_404(Dept, pk=id)
    if request.POST:
        form = DeptForm(data=request.POST, instance=dept)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = DeptForm(instance=dept)
    return render(request, 'form.html', {'form': form})

def test_mixed_form(request):
    if request.POST:
        form = MixedForm(request.POST)
        form.is_valid()
    else:
        form = MixedForm()
    return render(request, 'form.html', {'form': form})

def test_init_values(request):
    return render(request, 'form.html', {'form': InitialValueForm()})

def test_list_questions(request):
    return render(request, 'list.html', {
        'title': 'Questions',
        'href': 'test_tagging',
        'href_non_auto': 'test_tagging_non_auto',
        'object_list': Question.objects.all(),
        'create_new_href': 'test_tagging_new'
    })

def test_tagging_new(request):
    return test_tagging(request, None)

def test_tagging(request, id):
    if id is None:
        question = Question()
    else:
        question =  get_object_or_404(Question, pk=id)
    if request.POST:
        form = QuestionForm(data=request.POST, instance=question)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = QuestionForm(instance=question)
    return render(request, 'form.html', {'form': form})

def test_tagging_non_auto(request, id):
    if id is None:
        question = Question()
    else:
        question =  get_object_or_404(Question, pk=id)
    if request.POST:
        form = QuestionNonAutoForm(data=request.POST, instance=question)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = QuestionNonAutoForm(instance=question)
    return render(request, 'form.html', {'form': form})

def test_tagging_tags(request):
    tags = Tag.objects.all()
    results = [{'id': t.id, 'text': t.tag} for t in tags]
    return HttpResponse(json.dumps({'err': 'nil', 'results': results}), content_type='application/json')

def test_auto_multivalue_field(request):
    try:
        s = School.objects.get(id=1)
    except School.DoesNotExist:
        s = School(id=1)

    if request.POST:
        form = SchoolForm(data=request.POST, instance=s)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = SchoolForm(instance=s)
    return render(request, 'form.html', {'form': form})

def test_auto_heavy_perf(request):
    try:
        word = WordList.objects.get(kind='Word_Of_Day')
    except WordList.DoesNotExist:
        word = WordList(kind='Word_Of_Day')

    if request.POST:
        form = WordsForm(data=request.POST, instance=word)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = WordsForm(instance=word)
    return render(request, 'form.html', {'form': form})

def test_get_search_form(request):
    """
    Test a search form using GET. Issue#66
    """
    if request.GET:
        form = GetSearchTestForm(request.GET)
        if form.is_valid():
            results = Employee.objects.all()
            if form.cleaned_data['name'] != []:
                results = results.filter(name__in = form.cleaned_data['name'])
            if form.cleaned_data['dept'] != []:
                results = results.filter(dept__in = form.cleaned_data['dept'])
    else:
        form = GetSearchTestForm()
        results = Employee.objects.none()
    return render(request, 'formget.html', {'form': form, 'results' : results})

def test_issue_73(request):
    try:
        word = WordList.objects.get(kind='Word_Of_Day')
    except WordList.DoesNotExist:
        word = WordList(kind='Word_Of_Day')
        
    if request.POST:
        form = AnotherWordForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = AnotherWordForm(instance=word)
    return render(request, 'form.html', {'form': form})
