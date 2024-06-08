from django.core import serializers
from django.http import JsonResponse
from django import forms
import json

from .utils import is_ajax
from django_tables2 import SingleTableMixin
from django_filters.views import FilterView


class FilteredSingleTableView(SingleTableMixin, FilterView):
    form_helper_class = None

    def get_filterset(self, filterset_class):
        kwargs = self.get_filterset_kwargs(filterset_class)
        filterset = filterset_class(**kwargs)

        if 'exclude' in kwargs.keys():
            for excluded_field in kwargs['exclude']:
                filterset.form.fields[excluded_field].widget = forms.HiddenInput()

        if self.form_helper_class:
            filterset.form.helper = self.form_helper_class()

        return filterset


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

    def form_valid(self, form, response_data=None):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        self.object = form.save()
        if is_ajax(self.request):
            data = json.dumps(response_data, default=str) if response_data else serializers.serialize('json', [self.object, ])
            return JsonResponse(data, safe=False)
        else:
            return super().form_valid(form)


class AjaxableModelDeleteMixin:
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
        self.object.delete()
        if is_ajax(self.request):
            data = serializers.serialize('json', [self.object, ])
            return JsonResponse(data, safe=False)
        else:
            return super().form_valid(form)