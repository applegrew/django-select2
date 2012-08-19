from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from .forms import EmployeeForm
from .models import Employee

def test_auto_model_field(request):
    return render_to_response('list.html', RequestContext(request, {
    	'title': 'Employees',
    	'href': 'test_auto_model_field2',
    	'object_list': Employee.objects.all()
    	}))    

def test_auto_model_field1(request, id):
    emp =  Employee.objects.get(id=id)
    if request.POST:
        form = EmployeeForm(data=request.POST, instance=emp)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = EmployeeForm(instance=emp)
    return render_to_response('form.html', RequestContext(request, {'form': form}))    