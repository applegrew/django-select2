from django.contrib import admin
from .models import ClassRoom, Lab, Dept, Employee, Word, School
from .forms import SchoolForm


class SchoolAdmin(admin.ModelAdmin):

    form = SchoolForm

    class Media:
        js = ['jquery-1.7.2.min.js']


admin.site.register(ClassRoom)
admin.site.register(Lab)
admin.site.register(Dept)
admin.site.register(Employee)
admin.site.register(Word)
admin.site.register(School, SchoolAdmin)
