from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin

from .models import *


class DepartmentTabularInline(admin.TabularInline):
    model = Department

    fields = (
        'organization',
        'title_ar',
        'title_en',
    )

    autocomplete_fields = (
        'organization',
    )


class EmployeeTabularInline(admin.TabularInline):
    model = Employee

    fields = (
        'user',
        'first_name_en',
        'last_name_en',
        'job_title',
        'personal_picture',
        'nationality',
        'mobile',
    )

    autocomplete_fields = (
        'user',
        'department',
    )


class OrganizationResource(resources.ModelResource):
    class Meta:
        model = Organization
        import_id_fields = ('id',)
        fields = (
            'id',
            'name_ar',
            'name_en',
            'type',
            'city',
        )
        skip_unchanged = True
        report_skipped = True


class OrganizationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        'name_ar',
        'name_en',
        'type',
        'city',
    )

    list_filter = (
        'type',
        'city',
    )

    search_fields = list_display

    inlines = [DepartmentTabularInline, ]

    resource_class = OrganizationResource


class DepartmentAdmin(admin.ModelAdmin):
    list_display = DepartmentTabularInline.fields

    search_fields = DepartmentTabularInline.fields

    autocomplete_fields = DepartmentTabularInline.autocomplete_fields

    inlines = [EmployeeTabularInline, ]


class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        'first_name_en',
        'last_name_en',
        'job_title',
        'department',
        'nationality',
        'mobile',
    )

    list_filter = (
        'job_title',
        'nationality',
    )

    search_fields = (
        'user',
        'first_name_ar',
        'first_name_en',
        'last_name_ar',
        'last_name_en',
        'job_title',
        'department',
    )

    autocomplete_fields = EmployeeTabularInline.autocomplete_fields


class TaskAdmin(admin.ModelAdmin):
    list_display = (
        'description',
        'employee',
        'create_date',
        'due_date',
        'question',
        'status',
    )


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Task, TaskAdmin)

