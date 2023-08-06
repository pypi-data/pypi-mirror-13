from django import forms
from django_filters.widgets import BooleanWidget


class BooleanField(forms.BooleanField):
    widget = BooleanWidget


class ArrayDecimalField(forms.DecimalField):
    def clean(self, value):
        if value is None:
            return None

        out = []
        for val in value.split(','):
            out.append(super(ArrayDecimalField, self).clean(val))
        return out


class ArrayCharField(forms.CharField):
    def clean(self, value):
        if value is None:
            return None

        out = []
        for val in value.split(','):
            out.append(super(ArrayCharField, self).clean(val))
        return out
