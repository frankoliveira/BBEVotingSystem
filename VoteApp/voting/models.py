from django.db import models
from users.models import CustomUser
from .enums import CandidacyTypeEnum, VoteTypeEnum

class Election(models.Model):
    id_author = models.ForeignKey(CustomUser, related_name='elections', on_delete=models.DO_NOTHING, db_column='id_autor')
    tittle = models.CharField(verbose_name='Titulo', max_length=200, help_text="Máximo 200 caracteres", db_column='titulo')
    description = models.CharField(verbose_name='Descrição', max_length=300, help_text='Máximo 300 caracteres', db_column='descricao')
    creation = models.DateTimeField(verbose_name='Criação', auto_now=True, db_column='criacao')
    start = models.DateTimeField(verbose_name='Início', auto_now=False, db_column='inicio') 
    end = models.DateTimeField(verbose_name='Fim', auto_now=False, db_column='fim')
    last_change = models.DateTimeField(verbose_name='Última Alteração', auto_now=True, db_column='ultima_alteracao')
    #eligible_voters = models.CharField('Eleitores', max_length=100, db_column='eleitores')
    #eligible_voters = models.ManyToManyField(verbose_name='Eleitores', to=CustomUser, db_table='election_voters') 
    phe_public_key = models.CharField(verbose_name='Chave Pública (Paillier)', default='', max_length=500, db_column='phe_chave_publica')

    class Meta:
        verbose_name = 'Eleição'
        verbose_name_plural = 'Eleições'
        ordering = ['id']

    def __str__(self) -> str:
        return self.tittle
    
    @staticmethod
    def check_voting_permission(id_election: int, id_user: int):
        return ElectionVoter.objects.filter(id_election=id_election, id_user=id_user).exists()
    
    @staticmethod
    def get_election_by_id(id_election: int):
        try:
            election = Election.objects.get(id=id_election)
            return election
        except Election.DoesNotExist:
            return None

class Position(models.Model):
    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='positions', db_column='id_eleicao')
    order = models.IntegerField(verbose_name="Ordem", default=1, db_column='ordem')
    description = models.TextField(verbose_name="Descrição", max_length=100, db_column='descricao')
    last_change = models.DateTimeField(verbose_name='Útima alteração', auto_now=True, db_column='ultima_alteracao')

    class Meta:
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'
        ordering = ['id']

    def __str__(self) -> str:
        return self.description


class Candidacy(models.Model):
    CANDIDACY_TYPE_CHOICES = (
        (CandidacyTypeEnum.Candidate.value, 'Candidato'),
        (CandidacyTypeEnum.ElectoralPlate.value, 'Chapa')
    )

    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='candidacies', db_column='id_eleicao')
    id_position = models.ForeignKey(Position, on_delete=models.DO_NOTHING, related_name='candidacies', db_column='id_cargo')
    type = models.IntegerField(verbose_name="Tipo", choices=CANDIDACY_TYPE_CHOICES, db_column='tipo')
    number = models.IntegerField(verbose_name="Número", db_column='numero')
    name = models.CharField(verbose_name='Nome', max_length=100, help_text='Máximo 100 caracteres', db_column='Nome')
    description = models.CharField(verbose_name='Descrição', max_length=300, help_text='Máximo 300 caracteres', db_column='descricao')
    value = models.CharField(verbose_name='Valor', max_length=100, db_column='valor') #lista com candidatos
    received_votes = models.IntegerField(verbose_name="Votos recebidos", default=0, db_column='votos_recebidos')
    last_change = models.DateTimeField(verbose_name='Última alteração', auto_now=True, db_column='ultima_alteracao')

    class Meta:
        verbose_name = 'Candidatura'
        verbose_name_plural = 'Candidaturas'
        ordering = ['?']

class ElectionVoter(models.Model):
    '''
    Represents the eligible election voters.
    '''
    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='election_voters', db_column='id_eleicao')
    id_user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, db_column='id_autor')
    has_voted = models.BooleanField(verbose_name="Votou", default=False, db_column='votou')

    class Meta:
        verbose_name = 'Eleitor Elegível'
        verbose_name_plural = 'Eleitores Elegíveis'
        ordering = ['id']

class Vote(models.Model):
    VOTE_TYPE_CHOICES = (
        (VoteTypeEnum.Valid.value, 'Válido'),
        (VoteTypeEnum.Null.value, 'Nulo')
    )

    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='votes', db_column='id_eleicao')
    type = models.IntegerField(verbose_name="Tipo", choices=VOTE_TYPE_CHOICES, db_column='tipo')
    answer = models.CharField(verbose_name='Resposta', max_length=500, db_column='resposta')

class ElectionResult(models.Model):
    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, db_column='id_eleicao')
    result = models.CharField(verbose_name='Resultado', max_length=100, db_column='resultado')
    creation = models.DateTimeField(verbose_name='Criação', auto_now=False, db_column='criacao')
    
    class Meta:
        verbose_name = 'Resultado de Eleição'
        verbose_name_plural = 'Resultados de Eleições'
        ordering = ['id']
