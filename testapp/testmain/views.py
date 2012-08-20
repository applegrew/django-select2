from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from .forms import EmployeeForm #, DeptForm
from .models import Employee, Dept

def test_single_value_model_field(request):
    return render_to_response('list.html', RequestContext(request, {
    	'title': 'Employees',
    	'href': 'test_single_value_model_field1',
    	'object_list': Employee.objects.all()
    	}))    

def test_single_value_model_field1(request, id):
    emp =  get_object_or_404(Employee, pk=id)
    if request.POST:
        form = EmployeeForm(data=request.POST, instance=emp)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = EmployeeForm(instance=emp)
    return render_to_response('form.html', RequestContext(request, {'form': form}))


def test_multi_values_model_field(request):
    return render_to_response('list.html', RequestContext(request, {
    	'title': 'Departments',
    	'href': 'test_multi_values_model_field1',
    	'object_list': Dept.objects.all()
    	}))    

def test_multi_values_model_field1(request, id):
    dept =  get_object_or_404(Dept, pk=id)
    if request.POST:
        form = DeptForm(data=request.POST, instance=dept)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = DeptForm(instance=dept)
    return render_to_response('form.html', RequestContext(request, {'form': form}))

