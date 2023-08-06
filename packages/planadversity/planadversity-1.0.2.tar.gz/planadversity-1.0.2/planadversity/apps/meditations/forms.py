from django.core.urlresolvers import reverse
import floppyforms as forms

from .models import Response, Meditation


class ResponseForm(forms.ModelForm):
    #meditation = forms.IntegerField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Response
        exclude = ['user']

