from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .forms import EmployeeForm, DeptForm, MixedForm, InitialValueForm
from .models import Employee, Dept


def test_single_value_model_field(request):
    return render(request, 'list.html', {
        'title': 'Employees',
        'href': 'test_single_value_model_field1',
        'object_list': Employee.objects.all()
    })


def test_single_value_model_field1(request, id):
    emp = get_object_or_404(Employee, pk=id)
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
        'object_list': Dept.objects.all()
    })


def test_multi_values_model_field1(request, id):
    dept = get_object_or_404(Dept, pk=id)
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
