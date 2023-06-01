from crispy_forms.helper import FormHelper
from django import forms
from django.utils.safestring import mark_safe

from .models import Audit, Evidence


class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = '__all__'


class QuestionAnswersWidget(forms.RadioSelect):
    template_name = 'assessment/question_and_answers_field.html'

    def render(self, name, value, attrs=None, renderer=None):
        return super().render(name, value, attrs, renderer)


class AuditQuestionsForm(forms.Form):
    def __init__(self, audit, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audit = audit

        for question in self.audit.questions.all():
            answers = question.answers.all()
            choices = [(answer.pk, str(answer)) for answer in answers]
            choices.insert(0, (None, ' --- '))

            self.fields['q{}'.format(question.pk)] = forms.ChoiceField(
                label=question.prompt(),
                help_text=question.help_text(),
                required=True,
                choices=choices,
                widget=QuestionAnswersWidget(attrs={'question': question}),
            )
            self.fields['q{}'.format(question.pk)].question = question

            if question.get_the_answer():
                self.initial['q{}'.format(question.pk)] = question.get_the_answer().pk


class EvidenceForm(forms.ModelForm):
    question = None

    class Meta:
        model = Evidence
        fields = (
            'question',
            'type',
            'uploaded_file',
            'notes',
        )
        widgets = {
            'question': forms.HiddenInput,
        }

    def __init__(self, question, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.question = question
        self.initial['question'] = question
