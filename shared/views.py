from django.views.generic import TemplateView, FormView
from assessment.forms import AuditQuestionsForm
from assessment.models import Audit


class HomeView(FormView):
    template_name = 'shared/home.html'
    form_class = AuditQuestionsForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['audit'] = Audit.objects.first()
        return kwargs
