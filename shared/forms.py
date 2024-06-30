from django import forms


class DummyForm(forms.Form):
    pass


class MyDateTimeInput(forms.DateTimeInput):
    input_type = "datetime-local"
