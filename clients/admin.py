from django.contrib import admin
from .models import *


class OrganizationAdmin(admin.ModelAdmin):
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


class DepartmentAdmin(admin.ModelAdmin):
    list_display = (
        'organization',
        'title_ar',
        'title_en',
    )


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


admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Employee, EmployeeAdmin)
