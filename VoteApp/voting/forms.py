from voting.models import Election
from django import forms
from django.forms import ModelForm

class ElectionCreateForm(ModelForm):
    class Meta:
        model = Election
        fields = ['tittle', 'description', 'start', 'end']

class ElectionUpdtateForm(ModelForm):
    class Meta:
        model = Election
        fields = ['tittle', 'description', 'start', 'end']