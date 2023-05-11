from django.contrib import admin
from .models import *


class AssessmentAdmin(admin.ModelAdmin):
    list_filter = (
        'type',
    )

    list_display = (
        'title_ar',
        'title_en',
        'type',
        'derived_from',
        'created_by',
        'created_on',
    )

    date_hierarchy = 'created_on'


class SectionAdmin(admin.ModelAdmin):
    list_display = (
        'title_ar',
        'title_en',
        'sub_of',
        'display_order',
        'show_flag',
    )

    list_filter = (
        'show_flag',
    )


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'assessment',
        'prompt_ar',
        'prompt_en',
        'section',
        'display_order',
    )

    list_filter = (
        'section',
    )


class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'prompt_ar',
        'prompt_en',
        'selected_answer',
        'weight',
        'answered_by',
    )

    list_filter = (
        'selected_answer',
    )

    date_hierarchy = 'answered_on'


class EvidenceAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'type',
        'uploaded_file',
        'uploaded_by',
    )

    list_filter = (
        'type',
    )

    date_hierarchy = 'uploaded_on'


admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Evidence, EvidenceAdmin)
