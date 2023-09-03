from voting.models import Election
from django import forms
from django.forms import ModelForm

class ElectionCreateForm(ModelForm):
    class Meta:
        model = Election
        fields = ['tittle', 'description', 'start', 'end']
    #author = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING)
    #tittle = models.CharField('titulo', max_length=200, help_text="Máximo 200 caracteres")
    #description = models.CharField('descricao', max_length=300, help_text='Máximo 300 caracteres')
    #creation = models.DateTimeField('creation', auto_now=False)
    #start = models.DateTimeField('inicio', auto_now=False)
    #end = models.DateTimeField('fim', auto_now=False)
    #last_change = models.DateTimeField('ultima_alteracao', auto_now=True)