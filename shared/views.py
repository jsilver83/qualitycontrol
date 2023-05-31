from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, FormView
from assessment.forms import AuditQuestionsForm
from assessment.models import Audit, Answer


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
