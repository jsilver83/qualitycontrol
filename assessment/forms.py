from django import forms

from .models import Audit


class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = '__all__'


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
                widget=forms.RadioSelect(),
            )

            if question.get_the_answer():
                self.initial['q{}'.format(question.pk)] = question.get_the_answer().pk


        # for field in self.fields:
        #     print(field)
