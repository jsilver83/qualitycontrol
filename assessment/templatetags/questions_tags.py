from django import template
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from assessment.models import Answer, Question, Evidence, Section
from ..forms import EvidenceForm, SectionForm
from clients.forms import TaskForm

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def print_answer_weight(answer_pk):
    if answer_pk:
        answer = get_object_or_404(Answer, pk=answer_pk)
        if answer.is_best_answer():
            text_class = 'success'
        elif answer.weight:
            text_class = 'info'
        else:
            text_class = 'danger'
        if answer.weight is not None:
            return mark_safe(f'W: <b class="text-{text_class}">{answer.weight}</b>')
        else:
            return mark_safe(f'<em>{_("Not Weighted")}</em>')
    else:
        return '---'


@register.inclusion_tag('assessment/_create_evidence.html', takes_context=True)
def create_evidence(context, question):
    form = EvidenceForm(question, context.request.POST or None)

    return {
        'form': form,
        'question': question,
        'prefix': question.pk,
    }


@register.inclusion_tag('clients/_create_task.html', takes_context=True)
def create_task(context, question):
    form = TaskForm(question, context.request.POST or None)

    return {
        'form': form,
        'question': question,
        'prefix': question.pk,
    }


@register.inclusion_tag('assessment/_create_section.html', takes_context=True)
def create_section(context):
    form = SectionForm(context.request.POST or None)

    return {
        'section_form': form,
    }


@register.inclusion_tag('assessment/_delete_question.html', takes_context=True)
def delete_question(context, question):
    return {
        'question': question,
    }

