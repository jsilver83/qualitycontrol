from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import FormView, CreateView
from assessment.forms import AuditQuestionsForm, EvidenceForm
from assessment.models import Audit, Answer
from .mixins import AjaxableModelFormResponseMixin


class HomeView(LoginRequiredMixin, FormView):
    template_name = 'shared/home.html'
    form_class = AuditQuestionsForm
    success_url = '.'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['audit'] = Audit.objects.first()
        return kwargs

    def form_valid(self, form):
        for field in form.fields:
            the_question = form.fields[field].widget.attrs.get('question')
            the_answer = get_object_or_404(Answer, pk=form.cleaned_data.get(field))
            the_question.change_the_answer(the_answer, self.request.user)
        
        return super().form_valid(form)


class CreateEvidenceView(AjaxableModelFormResponseMixin, CreateView):
    template_name = 'assessment/question_and_answers_field.html'
    form_class = EvidenceForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['question'] = ''  # we are passing dummy value here that will be overridden by POST data
        return kwargs

    def form_valid(self, form):
        evidence = form.save(commit=False)
        evidence.uploaded_by = self.request.user
        return super().form_valid(form)
