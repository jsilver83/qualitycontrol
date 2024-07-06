import django_filters
from django.utils.translation import gettext_lazy as _
from django_select2.forms import Select2Widget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field

from .models import Audit
from django.contrib.auth import get_user_model
from clients.models import Organization


class S2Widget(Select2Widget):
    search_fields = [
        "title_en__icontains",
        "title_ar__icontains",
    ]

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.attrs = {'data-width': '100%'}


class AuditFilter(django_filters.FilterSet):
    class Meta:
        model = Audit
        fields = [
            'created_for',
            'created_by',
            'status',
            ]

    def __init__(self, exclude, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.Meta.exclude = exclude
        user_model = get_user_model()
        self.form.fields['created_by'].widget = S2Widget()
        self.form.fields['created_by'].queryset = user_model.objects.filter(
            employee__department__organization=self.request.user.employee.organization)
        self.form.fields['created_for'].widget = S2Widget()
        self.form.fields['created_for'].queryset = Organization.objects.all()


class Row(Div):
    css_class = 'row'


class AuditFilterFormHelper(FormHelper):
    form_method = 'GET'
    layout = Layout(
        Row(
            Field('type', wrapper_class='col-md-3 mb-0', css_class="form-control"),
            Field('created_for', wrapper_class='col-md-3 mb-0', css_class="form-control"),
            Field('created_by', wrapper_class='col-md-3 mb-0', css_class="form-control"),
            Field('status', wrapper_class='col-md-3 mb-0', css_class="form-control"),
        ),
        Submit('submit', _('Search'), wrapper_class='row', css_class='btn btn-primary float-right'),
    )


