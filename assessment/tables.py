import itertools

import django_tables2 as tables
from django_tables2 import TemplateColumn
from django_filters import FilterSet
from django.utils.translation import gettext_lazy as _

from .models import Question, Audit


class AuditTable(tables.Table):
    title = TemplateColumn(
        template_name='assessment/_audit_table_title_column.html',
        verbose_name=_('Title'),
    )
    submit = TemplateColumn(
        template_code=""" <a href='{% url "submit_assessment" record.pk %}'class="btn btn-md 
        {% if record.status == "DRAFT" %}{%else %}disabled {%endif%}" title="submit"><i class="fa fa-paper-plane"></i>
        </a> """,
        orderable=False,
        verbose_name=_('Fill'),
    )
    update_questions = TemplateColumn(
        template_code=""" <a href='{% url "questions" record.pk %}' class="btn btn-md 
        {% if record.status != "DRAFT" %}disabled {%endif%}" title="update"><i class="fa fa-edit"></i>
        </a>""",
        orderable=False,
        verbose_name=_('Modify'),
    )
    # derive = TemplateColumn(
    #     template_code=""" <a href='{% url "derive_assessment" record.pk %}' class="btn btn-md"
    #     title="Derive"><i class="fa fa-plus"></i></a>""",
    #     orderable=False,
    #     verbose_name=_('Derive'),
    # )
    detailed_report = TemplateColumn(
        template_code=""" <a href='{% url "view_assessment" record.pk %}'class="btn btn-md " 
        title="view"><i class="fa fa-eye"></i></a> """,
        orderable=False,
        verbose_name=_('Report'),
    )
    delete = TemplateColumn(
        template_code="""<form method="post" action='{% url "delete_assessment"  record.pk %}'>
                {% csrf_token %}
                <button type="submit" class="btn btn-danger btn-xs" title="Delete" 
                onclick="return confirm('Are you sure?');" audit_id={{record.pk}}>
                <i class="fa fa-trash"></i></button>
                </form> """,
        orderable=False,
        verbose_name=_('Delete'),
    )
    questions_count = tables.Column(verbose_name=_('Questions Count'))
    score_in_words = tables.Column(verbose_name=_('Score'), orderable=False)

    class Meta:
        model = Audit
        template_name = "django_tables2/bootstrap4.html"
        fields = ("title", "score_in_words", "questions_count", "created_for", "inspection_date", "status",)


class AssessmentDetailsTable(tables.Table):
    counter = tables.Column(verbose_name="#", empty_values=(), orderable=False)
    get_the_answer = tables.Column(verbose_name=_("Selected Answer"), orderable=False)
    prompt = tables.Column(verbose_name=_("Question"), orderable=False)
    score = tables.Column(verbose_name=_("Score"), orderable=False)
    evidences = TemplateColumn(verbose_name=_('Evidences'),
                               template_name='assessment/_audit_table_evidences_column.html', orderable=False)
    tasks = TemplateColumn(verbose_name=_("Tasks"), template_name='assessment/_audit_table_tasks_column.html',
                           orderable=False)

    class Meta:
        model = Question
        template_name = "django_tables2/bootstrap4.html"
        fields = ("counter", "section", "prompt", "get_the_answer", "score", "evidences", "tasks", )

    def render_counter(self):
        self.row_counter = getattr(self, 'row_counter',
                                   itertools.count(self.page.start_index()))
        return next(self.row_counter)


class QuestionTable(tables.Table):
    get_the_answer = tables.Column(verbose_name=_("Selected Answer"), orderable=False)
    update = TemplateColumn(
        template_code=""" <a 
            href='{% url "update_question" record.audit_id record.pk %}' class="btn btn-md" title="Update">
            <i class="fa fa-edit"></i>
            </a> """,
        orderable=False,
        verbose_name=_('Update'),
    )
    delete = TemplateColumn(
        template_code=""" <a 
            href='{% url "delete_question"  record.pk %}' class="btn btn-md confirm-delete" title="Delete" data-toggle="modal"
            data-target="#delete_modal{{record.pk}}" question_id={{record.pk}}>
            <i class="fa fa-trash" style="color:red"></i>
            </a> """,
        orderable=False,
        verbose_name=_('Delete'),
    )

    class Meta:
        model = Question
        template_name = "django_tables2/bootstrap4.html"
        fields = ("prompt", "get_the_answer", "is_bonus", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_columns['get_the_answer'].verbose_name = _("Selected Answer")


class QuestionFilter(FilterSet):
    class Meta:
        model = Question
        fields = ("prompt_en",)
