from django.contrib import admin
from .models import *


class QuestionTabularInlineAdmin(admin.TabularInline):
    model = Question

    fields = (
        'prompt_en',
        'section',
        'help_text_en',
        'display_order',
    )

    autocomplete_fields = (
        'audit',
        'section',
    )


class AnswerTabularInlineAdmin(admin.TabularInline):
    model = Answer

    autocomplete_fields = (
        'question',
        'answered_by',
    )

    fields = (
        'prompt_en',
        'weight',
        'selected_answer',
        'display_order',
    )


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'audit',
        'prompt',
        'section',
        'is_answered',
        'weight',
        'score',
        'is_scored',
        'display_order',
    )

    autocomplete_fields = QuestionTabularInlineAdmin.autocomplete_fields

    search_fields = (
        'audit',
        'prompt_ar',
        'prompt_en',
        'section',
    )

    inlines = [AnswerTabularInlineAdmin, ]


class AuditAdmin(admin.ModelAdmin):
    list_filter = (
        'type',
    )

    list_display = (
        'title_ar',
        'title_en',
        'type',
        'total_score',
        'weighted_total',
        'score_in_words',
        'derived_from',
        'created_by',
        'created_on',
    )

    date_hierarchy = 'created_on'

    search_fields = (
        'title_ar',
        'title_en',
        'type',
    )

    autocomplete_fields = (
        'created_for',
        'derived_from',
        'created_by',
        'updated_by',
    )

    inlines = [QuestionTabularInlineAdmin, ]


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

    search_fields = (
        'title_ar',
        'title_en',
    )


class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'question',
        'prompt',
        'selected_answer',
        'weight',
        'answered_by',
    )

    list_filter = (
        'selected_answer',
    )

    date_hierarchy = 'answered_on'

    autocomplete_fields = AnswerTabularInlineAdmin.autocomplete_fields


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

    autocomplete_fields = (
        'question',
    )


admin.site.register(Audit, AuditAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Evidence, EvidenceAdmin)
