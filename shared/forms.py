from django import forms

from clients.models import Organization


class DummyForm(forms.Form):
    pass


class MyDateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"


class ReportSearchForm(forms.Form):
    org_pk = forms.ChoiceField(
        choices=[(x.pk, str(x)) for x in Organization.objects.all()],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
