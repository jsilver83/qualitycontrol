import django_tables2 as tables
from django_tables2 import TemplateColumn
from django_filters import FilterSet
from django.core.paginator import Paginator

from .models import Question, Audit


class AuditTable(tables.Table):
    title = TemplateColumn(template_name='assessment/_audit_table_title_column.html')
    update_questions = TemplateColumn(template_code=""" <a 
    href='{% url "questions" record.pk %}' class="btn btn-md {% if record.status != "DRAFT" %}disabled {%endif%}" title="update"><i class="fa fa-edit"></i>
    </a>""", orderable=False)
    derive = TemplateColumn(template_code=""" <a 
    href='{% url "derive_assessment" record.pk %}' class="btn btn-md" title="Derive"><i class="fa fa-plus"></i>
    </a>""", orderable=False)
    submit = TemplateColumn(template_code=""" <a 
    href='{% url "submit_assessment" record.pk %}'class="btn btn-md {% if record.status != "DRAFT" %}disabled {%endif%}" title="submit"><i class="fa fa-paper-plane"></i>
    </a> """, orderable=False)
    detailed_report = TemplateColumn(template_code=""" <a 
    href='{% url "view_assessment" record.pk %}'class="btn btn-md " title="view"><i class="fa fa-eye"></i>
    </a> """, orderable=False)

    class Meta:
        model = Audit
        template_name = "django_tables2/bootstrap4.html"
        fields = ("title", "type", "created_for", "created_on", "created_by", "status", )



class AssessmentDetailsTable(tables.Table):
    get_the_answer = tables.Column(verbose_name="Selected Answer", orderable=False)
    prompt = tables.Column(verbose_name="Question", orderable=False)
    score = tables.Column(verbose_name="Score", orderable=False)
    evidences = TemplateColumn(template_name='assessment/_audit_table_evidences_column.html', orderable=False)
    tasks = TemplateColumn(verbose_name="Tasks", template_name='assessment/_audit_table_tasks_column.html', orderable=False)

    class Meta:
        model = Question
        template_name = "django_tables2/bootstrap4.html"
        fields = ("section", "prompt", "get_the_answer", "score", "evidences", "tasks", )


class QuestionTable(tables.Table):
    update = TemplateColumn(template_code=""" <a 
    href='{% url "update_question" record.audit_id record.pk %}' class="btn btn-md" title="Update">
    <i class="fa fa-edit"></i>
    </a> """, orderable=False)
    delete = TemplateColumn(template_code=""" <a 
    href='{% url "delete_question"  record.pk %}' class="btn btn-md confirm-delete" title="Delete" data-toggle="modal"
    data-target="#delete_modal{{record.pk}}" question_id={{record.pk}}>
    <i class="fa fa-trash" style="color:red"></i>
    </a> """, orderable=False)
    prompt = tables.Column(verbose_name="Question", orderable=False)

    class Meta:
        model = Question
        template_name = "django_tables2/bootstrap4.html"
        fields = ("prompt",)


class QuestionFilter(FilterSet):
    class Meta:
        model = Question
        fields = ("prompt_en",)