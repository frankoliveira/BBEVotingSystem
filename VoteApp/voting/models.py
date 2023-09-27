from django.db import models
from users.models import CustomUser
from .enums import OptionTypeEnum, VoteTypeEnum

class Election(models.Model):
    id_author = models.ForeignKey(CustomUser, related_name='elections', on_delete=models.DO_NOTHING, db_column='id_autor')
    tittle = models.CharField(verbose_name='Titulo', max_length=200, help_text="Máximo 200 caracteres", db_column='titulo')
    description = models.CharField(verbose_name='Descrição', max_length=300, help_text='Máximo 300 caracteres', db_column='descricao')
    creation = models.DateTimeField(verbose_name='Criação', auto_now=True, db_column='criacao')
    start = models.DateTimeField(verbose_name='Início', auto_now=False, db_column='inicio') 
    end = models.DateTimeField(verbose_name='Fim', auto_now=False, db_column='fim')
    last_change = models.DateTimeField(verbose_name='Última Alteração', auto_now=True, db_column='ultima_alteracao')
    voters = models.CharField('Eleitores', max_length=100, db_column='eleitores')
    phe_public_key = models.CharField('Chave Pública (Paillier)', max_length=500, db_column='phe_chave_publica')

    def create_vote():
        #verificar prazo da eleição
        #verificar se eleitor é válido
        pass

    class Meta:
        verbose_name = 'Eleição'
        verbose_name_plural = 'Eleições'
        ordering = ['id']

    def __str__(self) -> str:
        return self.tittle

class Question(models.Model):
    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='questions', db_column='id_eleicao')
    order = models.IntegerField(verbose_name="Ordem", db_column='ordem')
    description = models.TextField(verbose_name="Descrição", max_length=100, db_column='descricao')
    #active = models.BooleanField(verbose_name="Ativo", default=True, db_column='ativo')
    last_change = models.DateTimeField(verbose_name='Útima alteração', auto_now=True, db_column='ultima_alteracao')

    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'
        ordering = ['id']

    def __str__(self) -> str:
        return self.description
    

class Option(models.Model):
    TYPE_CHOICES = (
        (OptionTypeEnum.Candidate.value, 'Candidato'),
        (OptionTypeEnum.ElectoralPlate.value, 'Chapa')
    )
    #id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='options', db_column='id_eleicao')
    id_question = models.ForeignKey(Question, on_delete=models.DO_NOTHING, related_name='options', db_column='id_questao')
    order = models.IntegerField(verbose_name="Ordem", db_column='ordem')
    type = models.IntegerField(verbose_name="Tipo", choices=TYPE_CHOICES, db_column='tipo')
    value = models.CharField(verbose_name='Valor', max_length=100, db_column='valor') #lista com candidatos
    #received_votes = models.IntegerField(verbose_name="Votos recebidos", default=0, choices=TYPE_CHOICES, db_column='votos_recebidos')
    last_change = models.DateTimeField(verbose_name='Última alteração', auto_now=True, db_column='ultima_alteracao')

    class Meta:
        verbose_name = 'Opção'
        verbose_name_plural = 'Opções'
        ordering = ['id']

class ElectionResult(models.Model):
    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, db_column='id_eleicao')
    result = models.CharField(verbose_name='Resultado', max_length=100, db_column='resultado')
    creation = models.DateTimeField(verbose_name='Criação', auto_now=False, db_column='criacao')
    
    class Meta:
        verbose_name = 'Resultado de Eleição'
        verbose_name_plural = 'Resultados de Eleições'
        ordering = ['id']
