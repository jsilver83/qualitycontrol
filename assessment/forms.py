from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineRadios
from crispy_forms.layout import Layout, Fieldset, Submit, Div, Field
from django import forms
from django.forms import BaseFormSet
from django.utils.safestring import mark_safe
from django_select2 import forms as s2forms
from django.urls import reverse_lazy
from textwrap import indent

from .models import Audit, Evidence, Question, Answer, Section


class SectionWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "title_en__icontains",
        "title_ar__icontains",
    ]

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.attrs = {"style": "width: 500px"}

    def label_from_instance(self, obj):
        section = obj
        l = [section.title_en]
        while section.sub_of:
            l.append(section.sub_of.title_en)
            section = section.sub_of

        return ' | '.join(l) if obj.sub_of else obj.title_en


class SubWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "title_en__icontains",
        "title_ar__icontains",
    ]

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.attrs = {"style": "width: 300px"}

    def label_from_instance(self, obj):
        print(obj)
        section = obj
        l = [section.title_en]
        while section.sub_of:
            l.append(section.sub_of.title_en)
            section = section.sub_of

        return ' | '.join(l) if obj.sub_of else obj.title_en


class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['title_en', 'title_ar', 'type', 'created_for', 'derived_from', 'description_en', 'description_ar']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        derived_from = kwargs.pop('derived_from', None)
        super(AuditForm, self).__init__(*args, **kwargs)
        if derived_from:
            self.initial['derived_from'] = derived_from
            self.initial['type'] = derived_from.type
            self.initial['created_for'] = derived_from.created_for
            self.initial['description_en'] = derived_from.description_en
            self.initial['description_ar'] = derived_from.description_ar
        if not (user.is_superuser or user.is_staff):
            self.initial['type'] = user.employee.organization.type
            self.initial['created_for'] = user.employee.organization
            self.fields['type'].widget = forms.Field.hidden_widget()
            self.fields['created_for'].widget = forms.Field.hidden_widget()


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = [
            'title_en',
            'title_ar',
            'sub_of',
        ]
        widgets = {
            "sub_of": SubWidget,
        }


class CreateQuestionForm(forms.ModelForm):
    answers_type = forms.CharField(
        required=False,
        widget=forms.Select(choices=[
            ('yes_no', 'Yes/No'),
            ('yes_no_na', 'Yes/No N/A'),
            ('yes_no_moderate_na', 'Yes/No Moderate N/A'),
            ('custom', 'Custom'),
        ]),
        initial="custom")

    class Meta:
        model = Question
        fields = [
            'prompt_en',
            'prompt_ar',
            'help_text_en',
            'help_text_ar',
            'display_order',
            'section',
        ]
        widgets = {
            "section": SectionWidget,
            "prompt_en": forms.Textarea(attrs={"rows": 5, "cols": 20}),
            "prompt_ar": forms.Textarea(attrs={"rows": 5, "cols": 20}),
            "help_text_en": forms.Textarea(attrs={"rows": 5, "cols": 20}),
            "help_text_ar": forms.Textarea(attrs={"rows": 5, "cols": 20}),
        }


class ListQuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = [
            'prompt_en',
            'prompt_ar',
            'display_order',
            'section',
        ]


class RequiredFormSet(BaseFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormSet, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['prompt_en', 'prompt_ar', 'weight', 'display_order']


AnswerFormSet = forms.inlineformset_factory(Question, Answer, form=AnswerForm, extra=2)


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

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get('type'):
            if cleaned_data.get('type') == Evidence.Types.TEXT_NOTE and not cleaned_data.get('notes'):
                raise forms.ValidationError('Note field is required.')
            if cleaned_data.get('type') != Evidence.Types.TEXT_NOTE and not cleaned_data.get('uploaded_file'):
                raise forms.ValidationError('Attachment field is required.')
            
        return cleaned_data

