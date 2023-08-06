from django import forms
from django.db import models

from .widgets import MarkdownTextarea


class MarkdownFormField(forms.fields.CharField):
    def __init__(self, *args, **kwargs):
        widget = kwargs.get('widget', None)
        if not widget or not issubclass(widget, MarkdownTextarea):
            kwargs['widget'] = MarkdownTextarea
        super(MarkdownFormField, self).__init__(*args, **kwargs)


class MarkdownField(models.TextField):
    def formfield(self, form_class=MarkdownFormField, **kwargs):
        return super(MarkdownField, self).formfield(
            form_class=form_class, **kwargs)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(
        rules=[((MarkdownField,), [], {})],
        patterns=['^markymark\.fields']
    )
except ImportError:
    pass
