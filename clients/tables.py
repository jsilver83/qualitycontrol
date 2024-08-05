import django_tables2 as tables
from django_tables2 import TemplateColumn
from django_filters import FilterSet
from django.core.paginator import Paginator

from .models import Organization, Employee, Task


class OrganizationTable(tables.Table):
    departments = TemplateColumn(template_code="""<a href='{% url "update_departments" record.pk %}'
         class="btn btn-md " title="Departments"> <i class="fa fa-building"></i>
        </a> """, orderable=False)
    employees = TemplateColumn(template_code=""" <a href='{% url "employees_list" record.pk %}'
         class="btn btn-md " title="Employees"> <i class="fa fa-users"></i>
         </a> """, orderable=False)
    update_organization = TemplateColumn(template_code=""" <a href='{% url "update_organization" record.pk %}'
         class="btn btn-md " title="Update"> <i class="fa fa-edit"></i>
         </a>  """, orderable=False)

    class Meta:
        model = Organization
        template_name = "django_tables2/bootstrap4.html"
        fields = ("name_en", "name_ar", "commercial_licence_end_date", )


class EmployeeTable(tables.Table):
    update = TemplateColumn(template_code="""<a href='{% url "update_employee" record.pk %}'
         class="btn btn-md " title="update"> <i class="fa fa-edit"></i>
         </a>""", orderable=False)
    delete = TemplateColumn(template_code=""" <a href='{% url "delete_employee" record.pk %}'
         class="btn btn-md " title="delete"  onclick="return confirm(' you want to delete?');">
         <i class="fa fa-trash"></i>
         </a> """, orderable=False)

    class Meta:
        model = Employee
        template_name = "django_tables2/bootstrap4.html"
        fields = ("first_name", "last_name", "job_title", "department", )


class TaskTable(tables.Table):
    description = TemplateColumn(template_name='clients/_task_table_description_column.html')
    update_task = TemplateColumn(verbose_name="Update Task", template_code=""" <a href='{% url "update_task" record.pk %}'
         class="btn btn-md " title="Update"> <i class="fa fa-edit"></i>
         </a> """, orderable=False)
    complete_task = TemplateColumn(verbose_name="Complete Task", template_code=""" <a href='{% url "complete_task" record.pk %}'
         class="btn btn-md {% if record.status != "NEW" %} disabled {% endif %}" title="Complete Task">
         <i class="fa fa-check"></i>
         </a> """, orderable=False)
    cancel_task = TemplateColumn(verbose_name="Cancel Task", template_code=""" <a href='{% url "cancel_task" record.pk %}'
         class="btn btn-md {% if record.status != "NEW" %} disabled {% endif %} " title="Cancel Task">
         <i class="fa fa-times"></i>
         </a> """, orderable=False)

    class Meta:
        model = Task
        template_name = "django_tables2/bootstrap4.html"
        fields = ("employee", "description", "create_date", "due_date", "status", )






