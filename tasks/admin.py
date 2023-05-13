from django.contrib import admin
from .models import *


class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'description_ar',
        'description_en',
        'question',
        'due_date',
        'assigned_employee',
        'completion_date',
        'completed_by',
    ]

    date_hierarchy = 'created_on'


admin.site.register(Task, TaskAdmin)
