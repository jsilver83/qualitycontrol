from django.contrib import admin
from .models import *


class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'description',
        'question',
        'due_date',
        'assigned_employee',
        'completion_date',
        'completed_by',
    ]

    date_hierarchy = 'created_on'

    autocomplete_fields = (
        'question',
        'assigned_employee',
        'completed_by',
        'created_by',
        'updated_by',
    )


admin.site.register(Task, TaskAdmin)
