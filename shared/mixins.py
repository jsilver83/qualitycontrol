from django.core import serializers
from django.http import JsonResponse

from .utils import is_ajax


class AjaxableModelFormResponseMixin:
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if is_ajax(self.request):
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        self.object = form.save()
        if is_ajax(self.request):
            data = serializers.serialize('json', [self.object, ])
            return JsonResponse(data, safe=False)
        else:
            return super().form_valid(form)
