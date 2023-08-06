from django.forms import ModelForm

from .fields import LazyChoiceField


class LazyChoiceModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(LazyChoiceModelForm, self).__init__(*args, **kwargs)

        for field_name in self.fields:
            formfield = self.fields[field_name]
            if isinstance(formfield, LazyChoiceField):
                formfield.model = self.instance._meta.model
