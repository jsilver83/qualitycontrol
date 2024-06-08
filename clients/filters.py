import django_filters
from django_select2.forms import Select2Widget
from django.db import models
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field

from .models import Organization, Task, Employee


class DateInput(forms.DateInput):
    input_type = 'date'

class S2Widget(Select2Widget):
    search_fields = [
        "title_en__icontains",
        "title_ar__icontains",
    ]

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.attrs = {'data-width': '100%', 'class': 'form-control'}


class OrganizationFilter(django_filters.FilterSet):
    class Meta:
        model = Organization
        fields = [
            'type',
            ]


class TaskFilter(django_filters.FilterSet):
    due_date = django_filters.DateFilter(widget=DateInput(attrs={
        'class': 'datepicker'}))
    create_date = django_filters.DateFilter(widget=DateInput(attrs={
        'class': 'datepicker'}))

    class Meta:
        model = Task
        fields = [
            'employee',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form.fields['employee'].widget = S2Widget()
        self.form.fields['employee'].queryset = Employee.objects.filter(
            models.Q(id=self.request.user.employee.id)
            | models.Q(manager=self.request.user.employee))
        self.form.fields['employee'].widget.attrs['css_class'] = 'form-control'


class EmployeeFilter(django_filters.FilterSet):
    class Meta:
        model = Employee
        fields = [
            'job_title',
            'first_name_en',
            'last_name_en',
            ]
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            }
        }


class Row(Div):
    css_class = 'row'


class OrganizationFilterFormHelper(FormHelper):
    form_method = 'GET'
    layout = Layout(
        Row(
            Field('type', wrapper_class='col-md-3 mb-0', css_class="form-control"),
        ),
        Submit('submit', 'Apply Filters',wrapper_class='row', css_class='btn btn-primary float-right'),
    )


class TaskFilterFormHelper(FormHelper):
    form_method = 'GET'
    layout = Layout(
        Row(
            Field('status', wrapper_class='col-md-3 mb-0', css_class="form-control"),
            Field('employee', wrapper_class='col-md-3 mb-0', css_class="form-control"),
            Field('create_date', wrapper_class='col-md-3 mb-0', css_class="form-control"),
            Field('due_date', wrapper_class='col-md-3 mb-0', css_class="form-control"),
        ),
        Submit('submit', 'Apply Filters',wrapper_class='row', css_class='btn btn-primary float-right'),
    )


class EmployeeFilterFormHelper(FormHelper):
    form_method = 'GET'
    layout = Layout(
        Row(
            Field('job_title', wrapper_class='col-md-3 mb-0', css_class="form-control"),
            Field('first_name_en', wrapper_class='col-md-3 mb-0', css_class="form-control"),
            Field('last_name_en', wrapper_class='col-md-3 mb-0', css_class="form-control"),
        ),
        Submit('submit', 'Apply Filters',wrapper_class='row', css_class='btn btn-primary float-right'),
    )


