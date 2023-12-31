from django import template
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from assessment.models import Answer, Question, Evidence
from ..forms import EvidenceForm

register = template.Library()


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
