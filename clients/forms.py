from django import forms
from django.utils.safestring import mark_safe
from django_select2 import forms as s2forms
from django.urls import reverse_lazy
from django_select2 import forms as s2forms

from .models import Organization, Department, Employee, Task


class DateInput(forms.DateInput):
    input_type = 'date'


class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name_ar',
                  'name_en',
                  'type',
                  'city',
                  'commercial_registration_no',
                  'commercial_licence',
                  'commercial_licence_end_date',
                  'logo',
                  'address',
                  'address_on_map',
                  'website'
                  ]

        widgets = {
            "address": forms.Textarea(attrs={"rows": 5, "cols": 20}),
            "address_on_map": forms.Textarea(attrs={"rows": 5, "cols": 20}),
        }


class DepartmentInlineFormSet(forms.BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        super(DepartmentInlineFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            for name in form.fields:
                form.fields[name].widget.attrs.update({'class': 'form-control'})


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['title_en', 'title_ar', ]


DepartmentFormSet = forms.inlineformset_factory(Organization, Department, form=DepartmentForm, extra=1, formset=DepartmentInlineFormSet)


class CreateEmployeeForm(forms.ModelForm):
    user_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(max_length=50, widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = [
            'first_name_en',
            'first_name_ar',
            'last_name_en',
            'last_name_ar',
            'department',
            'job_title',
            'nationality',
            'mobile',
            'personal_picture',
            'manager',
        ]

    def __init__(self, *args, **kwargs):
        organization = kwargs.pop('organization', None)
        super(CreateEmployeeForm, self).__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(organization=organization)


class UpdateEmployeeForm(forms.ModelForm):
    user_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    password = forms.CharField(max_length=50, required=False, widget=forms.PasswordInput)

    class Meta:
        model = Employee
        fields = [
            'first_name_en',
            'first_name_ar',
            'last_name_en',
            'last_name_ar',
            'department',
            'job_title',
            'nationality',
            'mobile',
            'personal_picture',
            'manager',
        ]

    def __init__(self, associated_user, *args, **kwargs):
        super(UpdateEmployeeForm, self).__init__(*args, **kwargs)
        self.initial['user_name'] = associated_user.username
        self.initial['email'] = associated_user.email


class EmployeeListWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "first_name_en__icontains",
        "first_name_ar__icontains",
        "last_name_en__icontains",
        "last_name_ar__icontains",
    ]

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.attrs = {"style": "width: 400px"}

    def label_from_instance(self, obj):
        employee = obj
        return employee.full_name() + " (" + employee.department.title() + " )"


class TaskForm(forms.ModelForm):
    question_id = None

    class Meta:
        model = Task
        fields = [
            "question",
            "employee",
            "description",
            "due_date",
        ]
        widgets = {
            'due_date': DateInput(),
            'question': forms.HiddenInput,
            'employee': EmployeeListWidget,
        }

    def __init__(self, question_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question_id = question_id
        self.initial['question'] = question_id
        self.fields['employee'].widget.attrs['id'] = self.question_id


class UpdateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "description",
            "due_date",
            "status",
        ]
        widgets = {
            'due_date': DateInput(),
        }


class CompleteTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "notes",
            "attachment",
        ]






