import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView
from django_tables2 import SingleTableView

from django.db import models
from shared.mixins import AjaxableModelFormResponseMixin, FilteredSingleTableView
from .forms import *
from .tables import *
from .filters import *


# Create your views here.


class ListOrganizationView(FilteredSingleTableView):
    model = Organization
    template_name = "clients/organizations_list.html"
    table_class = OrganizationTable
    table_pagination = {
        "per_page": 20
    }
    filterset_class = OrganizationFilter
    form_helper_class = OrganizationFilterFormHelper


class CreateOrganizationView(CreateView):
    form_class = OrganizationForm
    template_name = "clients/create_organization.html"

    def get_success_url(self):
        return reverse('update_departments', args=(self.object.id, ))


class UpdateDepartmentsView(UpdateView):
    template_name = "clients/departments.html"
    form_class = OrganizationForm

    def get_success_url(self):
        success_url = reverse_lazy('organizations_list')
        return success_url

    def get_object(self, queryset=None):
        organization = Organization.objects.get(pk=self.kwargs['org_id'])
        return organization

    def get_context_data(self, **kwargs):
        context_data = super(UpdateDepartmentsView, self).get_context_data()
        context_data['organization'] = self.object
        if self.request.POST:
            context_data['department_formset'] = DepartmentFormSet(self.request.POST, instance=self.object)
        else:
            context_data['department_formset'] = DepartmentFormSet(instance=self.object)
        return context_data

    def form_valid(self, form):
        context_data = self.get_context_data()
        department_formset = context_data['department_formset']
        if department_formset.is_valid():
            department_formset.save()

        return super(UpdateDepartmentsView, self).form_valid(form)


class DetailOrganizationView(DetailView):
    pass


class UpdateOrganizationView(UpdateView):
    form_class = OrganizationForm
    template_name = "clients/create_organization.html"
    model = Organization

    def get_success_url(self):
        return reverse('update_departments', args=(self.object.id,))


class DeleteOrganizationView(DetailView):
    pass


class ListEmployeeView(FilteredSingleTableView):
    model = Employee
    template_name = "clients/employees_list.html"
    table_class = EmployeeTable
    table_pagination = {
        "per_page": 20
    }
    filterset_class = EmployeeFilter
    form_helper_class = EmployeeFilterFormHelper


    def get_queryset(self):
        organization = Organization.objects.get(id=self.kwargs['org_id'])
        employees = Employee.objects.filter(department__organization=organization)
        return employees

    def get_context_data(self, **kwargs):
        context = super(ListEmployeeView, self).get_context_data(**kwargs)
        context['organization'] = Organization.objects.get(id=self.kwargs['org_id'])
        return context


class CreateEmployeeView(CreateView):
    form_class = CreateEmployeeForm
    template_name = "clients/create_employee.html"

    def get_success_url(self):
        return reverse('employees_list', args=(self.kwargs['org_id'],))

    def get_form_kwargs(self):
        kwargs = super(CreateEmployeeView, self).get_form_kwargs()
        kwargs['organization'] = Organization.objects.get(id=self.kwargs['org_id'])
        return kwargs

    def form_valid(self, form):
        if form.is_valid():
            form_data = form.cleaned_data
            added_employee = form.save()
            associated_user = User.objects.create_user(username=form_data['user_name'],
                                                       email=form_data['email'],
                                                       password=form_data['password'],
                                                       )
            added_employee.user = associated_user
            added_employee.save()
        return super(CreateEmployeeView, self).form_valid(form)


class UpdateEmployeeView(UpdateView):
    form_class = UpdateEmployeeForm
    template_name = "clients/update_employee.html"
    model = Employee

    def get_success_url(self):
        return reverse('employees_list', args=(self.object.department.organization.id,))

    def get_form_kwargs(self):
        kwarg = super(UpdateEmployeeView, self).get_form_kwargs()
        kwarg['associated_user'] = User.objects.get(pk=self.object.user.pk)
        return kwarg

    def form_valid(self, form):
        if form.is_valid():
            form_data = form.cleaned_data
            updated_employee = form.save()
            updated_employee.user.user_name = form_data['user_name']
            updated_employee.user.user_name = form_data['email']
            updated_employee.user.user_name = form_data['password']
            updated_employee.save()
        return super(UpdateEmployeeView, self).form_valid(form)


class DeleteEmployeeView(DeleteView):
    model = Employee

    def get_success_url(self):
        return reverse('employees_list', args=(self.object.department.organization.id,))

    def get(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class CreateTaskView(AjaxableModelFormResponseMixin, CreateView):
    template_name = 'clients/create_task.html'
    form_class = TaskForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['question_id'] = self.kwargs['question_pk']
        return kwargs

    def form_valid(self, form):
        task = form.save()
        form.cleaned_data['employee_name'] = task.employee.first_name()
        task.status = "NEW"
        task.create_date = datetime.date.today()
        response_data = {
            "pk": task.pk,
            'employee': task.employee.full_name(),
            'status': task.get_status_display(),
            'due_date': task.due_date,
        }
        return super().form_valid(form, response_data)


class ListTaskView(FilteredSingleTableView):
    model = Task
    template_name = "clients/tasks_list.html"
    table_class = TaskTable
    table_pagination = {
        "per_page": 20
    }
    filterset_class = TaskFilter
    form_helper_class = TaskFilterFormHelper


    def get_queryset(self):
        queryset = (Task.objects.filter(models.Q(employee=self.request.user.employee)
                                       | models.Q(employee__in=self.request.user.employee.responsible_for.all()))
                    .order_by('-due_date'))
        return queryset


class DetailTaskView(DetailView):
    model = Task
    template_name = "clients/view_task.html"


class UpdateTaskView(UpdateView):
    model = Task
    form_class = UpdateTaskForm
    template_name = "clients/update_task.html"
    success_url = reverse_lazy("tasks_list")


class CompleteTaskView(UpdateView):
    model = Task
    form_class = CompleteTaskForm
    template_name = "clients/update_task_status.html"
    success_url = reverse_lazy("tasks_list")

    def form_valid(self, form):
        if form.is_valid():
            task = form.save()
            task.status = "DONE"
            task.save()
        return super().form_valid(form)


class CancelTaskView(UpdateView):
    model = Task
    form_class = CompleteTaskForm
    template_name = "clients/update_task_status.html"
    success_url = reverse_lazy("tasks_list")

    def form_valid(self, form):
        if form.is_valid():
            task = form.save()
            task.status = "CANCELLED"
            task.save()
        return super().form_valid(form)



