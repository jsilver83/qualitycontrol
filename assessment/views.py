import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django_tables2 import SingleTableView, MultiTableMixin
from django_tables2.export.views import ExportMixin

from shared.mixins import AjaxableModelFormResponseMixin, AjaxableModelDeleteMixin, FilteredSingleTableView
from .filters import *
from .forms import AuditForm, SectionForm, CreateQuestionForm, AnswerFormSet
from .models import Question, Answer
from .tables import QuestionTable, AuditTable, AssessmentDetailsTable


class ListAuditView(LoginRequiredMixin, FilteredSingleTableView):
    template_name = "assessment/audits.html"
    model = Audit
    table_class = AuditTable
    filterset_class = AuditFilter
    form_helper_class = AuditFilterFormHelper

    table_pagination = {
        "per_page": 20
    }

    def get_queryset(self):
        queryset = Audit.objects.filter(
            status__in=[
                Audit.Status.DRAFT,
                Audit.Status.SUBMITTED,
            ],
        )
        if self.request.user.is_superuser or self.request.user.is_staff:
            pass
        else:
            # employee = Employee.get_employee(self.request.user)
            queryset = queryset.filter(created_by=self.request.user)

        return queryset

    def get_table_kwargs(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return {
                'exclude': (
                    # 'created_by',
                )
            }
        else:
            return {
                'exclude': (
                    'created_by',
                    # 'type',
                    # 'created_for',
                )
            }

    def get_filterset_kwargs(self, filterset_class):
        filterset_kwargs = super().get_filterset_kwargs(filterset_class)
        if self.request.user.is_superuser or self.request.user.is_staff:
            filterset_kwargs['exclude'] = []

        else:
            filterset_kwargs['exclude'] = [
                'created_by'
            ]

        return filterset_kwargs


class DetailAssessmentView(MultiTableMixin, TemplateView):
    template_name = "assessment/view_assessment.html"
    audit = None
    sections = []

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.audit = Audit.objects.get(id=self.kwargs['audit_id'])
        self.sections = self.audit.get_sections()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['audit'] = self.audit
        context['root_sections'] = self.sections
        tables_names = {}
        for table in context['tables']:
            tables_names[int(table.prefix)] = table
        context['tables'] = tables_names
        chart_data = self.audit.get_chart_data()
        context['labels'], context['scores'] = json.dumps(chart_data[0]), json.dumps(chart_data[1])
        context['full_marks_100'] = json.dumps([100 for x in chart_data[1]])
        context['full_marks'] = json.dumps([104 for x in chart_data[1]])
        return context

    def get_tables(self):
        tables = []
        for sections in self.sections.values():
            for section in sections:
                questions = Question.objects.filter(audit=self.audit, section=section)
                table = AssessmentDetailsTable(data=questions, prefix=f"{section.id}")
                table.exclude = ('section', )
                tables.append(table)

        return tables


class DetailAssessmentExportView(ExportMixin, SingleTableView):
    table_class = AssessmentDetailsTable

    def get_queryset(self):
        return Question.objects.filter(audit=self.kwargs['audit_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['audit'] = Audit.objects.get(id=self.kwargs['audit_id'])
        return context

    def get_table_kwargs(self):
        return {
            'exclude': ('evidences', 'tasks', )
        }


class CreateAssessmentDeriveView(ListView):
    template_name = "assessment/create_assessment_derive.html"
    model = Audit
    context_object_name = 'audits'

    def get_queryset(self):
        return Audit.objects.filter(status=Audit.Status.TEMPLATE)


class CreateAssessmentView(CreateView):
    template_name = "assessment/create_assessment.html"
    form_class = AuditForm

    def get_form_kwargs(self):
        kwarg = super(CreateAssessmentView, self).get_form_kwargs()
        kwarg['user'] = self.request.user
        if "audit_id" in self.kwargs:
            audit_id = self.kwargs['audit_id']
            kwarg['derived_from'] = Audit.objects.get(pk=audit_id)

        return kwarg

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "audit_id" in self.kwargs:
            audit_id = self.kwargs['audit_id']
            context['derived_from'] = Audit.objects.get(pk=audit_id)
        return context

    def get_success_url(self):
        return reverse_lazy('assessments_list')
    
    def form_valid(self, form):
        if form.is_valid():
            form.instance.created_by = self.request.user
            if not (self.request.user.is_superuser or self.request.user.is_staff):
                self.initial['type'] = self.request.user.employee.organization.type
                self.initial['created_for'] = self.request.user.employee.organization
            audit = form.instance.save()
            if form.instance.derived_from:
                derived_from_questions = Question.objects.filter(audit=form.instance.derived_from)
                for question in derived_from_questions:
                    answers = Answer.objects.filter(question=question)
                    question.pk = None
                    question.audit = form.instance
                    question.save()
                    for answer in answers:
                        answer.pk = None
                        answer.question = question
                        answer.selected_answer = False
                        answer.answered_by = None
                        answer.answered_on = None
                        answer.save()

        return super(CreateAssessmentView, self).form_valid(form)


class ListQuestionView(MultiTableMixin, TemplateView):
    template_name = "assessment/questions.html"

    def dispatch(self, request, *args, **kwargs):
        self.audit = Audit.objects.get(id=self.kwargs['audit_id'])
        self.sections = self.audit.get_sections()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['audit'] = self.audit
        context['all_questions'] = Question.objects.filter(audit=self.audit)
        context['root_sections'] = self.sections
        if "tables" in context:
            tables_names = {}
            for table in context['tables']:
                tables_names[int(table.prefix)] = table
            context['tables'] = tables_names
        return context

    def get_tables(self):
        tables = []
        for sections in self.sections.values():
            for section in sections:
                questions = Question.objects.filter(audit=self.audit, section=section)
                tables.append(QuestionTable(data=questions, prefix=f"{section.id}"))

        return tables


class CreateSectionView(AjaxableModelFormResponseMixin, CreateView):
    template_name = "assessment/create_section.html"
    form_class = SectionForm


class CreateQuestionView(SuccessMessageMixin, CreateView):
    template_name = "assessment/create_question.html"
    form_class = CreateQuestionForm
    success_message = "Question was created successfully"

    def get_context_data(self, **kwargs):
        context_data = super(CreateQuestionView, self).get_context_data()
        context_data['audit'] = Audit.objects.get(id=self.kwargs['audit_id'])
        if self.request.POST:
            context_data['answer_formset'] = AnswerFormSet(self.request.POST)
        else:
            context_data['answer_formset'] = AnswerFormSet()
        return context_data

    def get_success_url(self):
        success_url = reverse_lazy('questions', args=(self.kwargs['audit_id'],))
        if self.request.method == 'POST' and 'save_and_new' in self.request.POST:
            success_url = reverse_lazy('create_question', args=(self.kwargs['audit_id'],))
        return success_url

    def form_valid(self, form):
        context_data = self.get_context_data()
        if form.is_valid():
            form.instance.audit = Audit.objects.filter(id=self.kwargs['audit_id']).first()
            answer_formset = context_data['answer_formset']

            form.instance.created_by = self.request.user
            question = form.save()

            if self.request.POST['answers_type'] != "custom":
                self.generate_answer(question, self.request.POST['answers_type'])

            else:

                if answer_formset.is_valid():
                    answer_formset.instance = question
                    answer_formset.save()


        return super(CreateQuestionView, self).form_valid(form)

    def generate_answer(self, question, answers_type):
        if answers_type == "yes_no":
            Answer.objects.bulk_create([
                Answer(prompt_en="Yes", weight=2, display_order=1, question=question),
                Answer(prompt_en="No", weight=0, display_order=2, question=question),
            ])
        if answers_type == "yes_no_na":
            Answer.objects.bulk_create([
                Answer(prompt_en="Yes", weight=2, display_order=1, question=question),
                Answer(prompt_en="No", weight=0, display_order=2, question=question),
                Answer(prompt_en="N/A", display_order=3, question=question),
            ])
        if answers_type == "yes_no_moderate_na":
            Answer.objects.bulk_create([
                Answer(prompt_en="Yes", weight=2, display_order=1, question=question),
                Answer(prompt_en="No", weight=0, display_order=2, question=question),
                Answer(prompt_en="Moderate", weight=1, display_order=3, question=question),
                Answer(prompt_en="N/A", display_order=4, question=question),
            ])


class UpdateQuestionView(UpdateView):
    template_name = "assessment/create_question.html"
    form_class = CreateQuestionForm

    def get_object(self, queryset=None):
        question = Question.objects.get(pk=self.kwargs['question_id'])
        return question

    def get_context_data(self, **kwargs):
        context_data = super(UpdateQuestionView, self).get_context_data()
        context_data['audit'] = Audit.objects.get(id=self.kwargs['audit_id'])
        if self.request.POST:
            context_data['answer_formset'] = AnswerFormSet(self.request.POST, instance=self.object)
        else:
            context_data['answer_formset'] = AnswerFormSet(instance=self.object)
        context_data['answer_formset'].extra = 0
        return context_data

    def get_success_url(self):
        success_url = reverse_lazy('questions', args=(self.kwargs['audit_id'],))
        if self.request.method == 'POST' and 'save_and_new' in self.request.POST:
            success_url = reverse_lazy('create_question', args=(self.kwargs['audit_id'],))
        return success_url

    def form_valid(self, form):
        context_data = self.get_context_data()
        if form.is_valid():
            form.instance.audit = Audit.objects.filter(id=self.kwargs['audit_id']).first()
            answer_formset = context_data['answer_formset']

            form.instance.updated_by = self.request.user
            question = form.save()
            answer_formset.instance = question
            answer_formset.save()

        return super(UpdateQuestionView, self).form_valid(form)


class DetailQuestionView(DetailView):
    template_name = "assessment/view_question.html"

    def get_object(self, queryset=None):
        question = Question.objects.get(pk=self.kwargs['question_id'])
        return question

    def get_context_data(self, **kwargs):
        context_data = super(DetailQuestionView, self).get_context_data()
        context_data['audit'] = Audit.objects.get(id=self.kwargs['audit_id'])
        context_data['answers'] = Answer.objects.filter(question=self.kwargs['question_id'])
        return context_data


class DeleteAuditView(View):

    def post(self, request, *args, **kwargs):
        audit = get_object_or_404(Audit, pk=self.kwargs['pk'])
        audit.delete()
        return redirect(reverse_lazy('assessments_list'))


class DeleteQuestionView(AjaxableModelDeleteMixin, DeleteView):
    model = Question
