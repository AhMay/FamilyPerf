from django import forms
from . import models

class PerfRecordForm(forms.Form):
    name = forms.CharField()
    score_up = forms.IntegerField()
    score_down = forms.IntegerField()
    score = forms.IntegerField(required=False)
    description = forms.CharField(required=False)

class PerfItemForm(forms.ModelForm):
    class Meta:
        model = models.PerfItem
        exclude = ['member']