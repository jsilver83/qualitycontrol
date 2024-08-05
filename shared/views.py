import json

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView, TemplateView
from assessment.forms import AuditQuestionsForm, EvidenceForm
from clients.forms import TaskForm
from assessment.models import Audit, Answer, Stats
from clients.models import Organization
from .forms import ReportSearchForm
from .mixins import AjaxableModelFormResponseMixin
from .models import Report


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "shared/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['strengths'] = Stats.get_strengths()[0:10]
        context['weaknesses'] = Stats.get_weaknesses()[0:10]
        context['top_unanswered_questions'] = Stats.get_top_unanswered_questions()[0:10]

        context['users_count'] = Stats.users_count()
        context['all_organizations_count'] = Stats.all_organizations_count()
        context['visited_organizations_count'] = Stats.visited_organizations_count()
        context['unvisited_organizations_count'] = context['all_organizations_count'] - context[
            'visited_organizations_count']
        context['inspection_visits_count'] = Stats.inspection_visits_count()

        return context


class SubmitAssessmentView(LoginRequiredMixin, FormView):
    template_name = 'shared/submit_assessment.html'
    form_class = AuditQuestionsForm
    success_url = reverse_lazy('assessments_list')
    audit = None

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.audit = get_object_or_404(Audit, id=self.kwargs['audit_id'])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['audit'] = self.audit
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['audit'] = self.audit
        return context

    def form_valid(self, form):
        for field in form.fields:
            the_question = form.fields[field].widget.attrs.get('question')
            the_answer = get_object_or_404(Answer, pk=form.cleaned_data.get(field))
            the_question.change_the_answer(the_answer, self.request.user)

        if 'submit' in self.request.POST:
            self.audit.status = Audit.Status.SUBMITTED

        self.audit.updated_by = self.request.user
        self.audit.save()

        return super().form_valid(form)


class CreateEvidenceView(LoginRequiredMixin, AjaxableModelFormResponseMixin, CreateView):
    # permission_required = 'evidence.can_add_evidence'
    template_name = 'assessment/question_and_answers_field.html'
    form_class = EvidenceForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['question'] = ''  # we are passing dummy value here that will be overridden by POST data
        return kwargs

    def form_valid(self, form, response_data=None):
        evidence = form.save()
        evidence.uploaded_by = self.request.user
        response_data = {
            "pk": evidence.pk,
            "type": evidence.get_type_display(),
            "uploaded_file": evidence.uploaded_file,
            "notes": evidence.notes,
        }
        return super().form_valid(form, response_data)


class OrganizationReportView(LoginRequiredMixin, TemplateView):
    template_name = 'shared/organization_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ReportSearchForm(self.request.GET or None)

        selected_org_pk = self.request.GET.get('org_pk', None)
        if selected_org_pk:
            org = get_object_or_404(Organization, pk=selected_org_pk)
            context['organization'] = org
            context['labels'], context['scores'] = Report.get_org_performance(org=org)
            context['labels'], context['scores'] = json.dumps(context['labels']), json.dumps(context['scores'])
        return context
