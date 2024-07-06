import json

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, CreateView, TemplateView
from assessment.forms import AuditQuestionsForm, EvidenceForm
from clients.forms import TaskForm
from assessment.models import Audit, Answer
from .mixins import AjaxableModelFormResponseMixin


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "shared/home.html"


class SubmitAssessmentView(LoginRequiredMixin, FormView):
    template_name = 'shared/submit_assessment.html'
    form_class = AuditQuestionsForm
    success_url = '.'
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


class HomeView2(TemplateView):
    template_name = "shared/home2.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = Audit.objects.get(pk=23).get_chart_data()
        context['labels'], context['scores'] = json.dumps(data[0]), json.dumps(data[1])
        print(data)
        return context
