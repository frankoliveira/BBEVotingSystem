from voting.models import Election, ElectionVoter, Position, Candidacy
from users.models import CustomUser
from .enums import CandidacyTypeEnum
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

class PositionCreateForm(ModelForm):
    class Meta:
        model = Position
        fields = ['id_election', 'order', 'name']

class PositionUpdateForm(ModelForm):
    class Meta:
        model = Position
        fields = ['order', 'name']

class CandidacyCreateForm(ModelForm):
    class Meta:
        model = Candidacy
        fields = ['id_election', 'id_position', 'type', 'number', 'name', 'description']

        '''
        fields = ['id_election', 'id_position', 'candidates', 'type', 'number', 'name', 'description']
        CANDIDACY_TYPE_CHOICES = (
            (CandidacyTypeEnum.Candidate.value, 'Candidato'),
            (CandidacyTypeEnum.ElectoralPlate.value, 'Chapa')
        )
        candidates = forms.ModelMultipleChoiceField(label='Candidatos', queryset=CustomUser.objects.all())
        type = forms.ChoiceField(choices=CANDIDACY_TYPE_CHOICES)
        '''