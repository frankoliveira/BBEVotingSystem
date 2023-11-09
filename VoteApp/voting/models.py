from django.db import models
from users.models import CustomUser
from .enums import CandidacyTypeEnum, ElectionPhaseEnum
from security.models import PheManager
from phe import paillier, PaillierPrivateKey, PaillierPublicKey, EncryptedNumber
import base64, json
import uuid
from datetime import datetime

class Election(models.Model):
    ELECTION_PHASE = (
        (ElectionPhaseEnum.PreVoting.value, 'Pré-votação'),
        (ElectionPhaseEnum.Voting.value, 'Votação'),
        (ElectionPhaseEnum.PosVoting.value, 'Pós-votação')
    )

    id_author = models.ForeignKey(CustomUser, related_name='elections', on_delete=models.DO_NOTHING, db_column='id_autor')
    tittle = models.CharField(verbose_name='Titulo', max_length=200, help_text="Máximo 200 caracteres", db_column='titulo')
    description = models.CharField(verbose_name='Descrição', max_length=300, help_text='Máximo 300 caracteres', db_column='descricao')
    creation = models.DateTimeField(verbose_name='Criação', auto_now=True, db_column='criacao')
    start = models.DateTimeField(verbose_name='Início', auto_now=False, db_column='inicio') 
    end = models.DateTimeField(verbose_name='Fim', auto_now=False, db_column='fim')
    last_change = models.DateTimeField(verbose_name='Última Alteração', auto_now=True, db_column='ultima_alteracao')
    phase = models.IntegerField(verbose_name="Fase", choices=ELECTION_PHASE, default=ElectionPhaseEnum.PreVoting.value, db_column='fase')
    guid = models.CharField(verbose_name='guid', default='', max_length=500, db_column='guid')

    class Meta:
        verbose_name = 'Eleição'
        verbose_name_plural = 'Eleições'
        ordering = ['id']

    def __str__(self) -> str:
        return self.tittle
    
    def save(self, *args, **kwargs):
        if not self.pk:
            #ações antes de savar no banco
            self.creation = datetime.now()
            self.guid = uuid.uuid4()
        super(Election, self).save(*args, **kwargs)
        self.generate_phe_keys()

    @staticmethod
    def get_element_by_id(id: int):
        try:
            election = Election.objects.get(id=id)
            return election
        except Election.DoesNotExist:
            return None
    
    @staticmethod
    def check_voter_permission(id_election: int, id_user: int) -> bool:
        '''
        Retorna True caso o eleitor tenha permissão para votar.
        '''
        return ElectionVoter.check_if_element_exists(id_election=id_election, id_user=id_user)
    
    def is_in_voting_period(self):
        '''
        Verifica se ainda é possível votar na eleição.
        '''
        from datetime import datetime
        from datetime import timezone
        date_now = datetime.now(tz=timezone.utc)
        
        if date_now < self.start or date_now > self.end:
            return False
        
        return True
    
    def get_positions(self):
        '''
        Obtem os cargos de uma eleição.
        '''
        positions = Position.objects.filter(id_election=self.id) #retorna uma queryset vazia se não tiver resultados
        if len(positions)>0:
            return [position for position in positions]
        return None
    
    def check_vote_validity(self, vote_form) -> bool:
        election_positions = self.get_positions()

        for position in election_positions:
            #verifica se as perguntas foram respondidas e se possuem um valor válido
            if (not f'{position.id}' in vote_form) or (not vote_form[f'{position.id}']):
                return False
            #Verifica se foi escolhido uma candidatura válida
            if int(vote_form[f'{position.id}'])!=0 and not Candidacy.check_if_element_exists(self.id, position.id, int(vote_form[f'{position.id}'])):
                return False
            
        return True

    def process_vote(self, id_user: int, vote_form):
        from phe import EncryptedNumber
        try:
            election_positions = self.get_positions()                
            public_key = self.load_public_key()
            #private_key = self.load_private_key() #apenas para teste
            vote_dict = {
                "id_eleicao": self.id,
                "cargos": []
            }
        
            voted_candidacies = []

            for position in election_positions:
                number_candidacy_voter_choice = int(vote_form[f'{position.id}'])
                candidacies = position.get_candidacies()
                position_vote = {}
                position_vote['id_cargo'] = position.id
                position_vote['descricao_cargo'] = position.description
                position_vote['voto'] = {}

                for candidacy in candidacies:
                    vote = 0
                    if number_candidacy_voter_choice==candidacy.number:
                        voted_candidacies.append(candidacy)
                        vote = 1
                    enc_vote = public_key.encrypt(vote)
                    #decrypted = private_key.decrypt(enc_vote)
                    #print("valor descriptado: ", decrypted)
                    position_vote['voto'][f'{candidacy.number}'] = enc_vote.ciphertext()

                vote_dict['cargos'].append(position_vote)
            
            vote_string_format = json.dumps(vote_dict)
            #enviar voto = vote_string_format

            for candidacy in voted_candidacies:
                ciphertext = int(candidacy.received_votes)
                encrypted_received_votes = EncryptedNumber(public_key=public_key, ciphertext=ciphertext) + 1
                candidacy.received_votes = str(encrypted_received_votes.ciphertext())
                candidacy.save()
                #print("votos recebidos: ", private_key.decrypt(encrypted_received_votes))

            self.update_voted_candidacies(public_key=public_key, voted_candidacies=voted_candidacies)
            self.create_vote(voter_answer=vote_string_format)
            self.set_has_voted(id_user=id_user)
            return "transacao_id"
                
        except Exception as ex:
            print("erro ao processar voto: ", ex)
            return None
    
    def generate_phe_keys(self):
        '''
        Gera chaves PHE - Paillier Homomorphic Encryption
        '''
        import os
        public_key, private_key = PheManager.new_keys_512()
        str_phe_public_key = PheManager.generate_str_public_key(public_key=public_key)
        str_phe_private_key = PheManager.generate_str_private_key(private_key=private_key)
        path_keys = f'media/election_keys/{self.guid}/'
        os.mkdir(path_keys)

        with open(path_keys+f'/private_phe_{self.id}.txt', 'w') as new_file:
            new_file.write(str_phe_private_key)
        
        with open(path_keys+f'/public_phe_{self.id}.txt', 'w') as new_file:
            new_file.write(str_phe_public_key)

    def load_private_key(self):
        with open(f'media/election_keys/{self.guid}/private_phe_{self.id}.txt', 'r') as file:
            data = file.read()
        return PheManager.load_private_key_from_str(private_key=data)
    
    def load_public_key(self):
        with open(f'media/election_keys/{self.guid}/public_phe_{self.id}.txt', 'r') as file:
            data = file.read()
        return PheManager.load_public_key_from_str(public_key=data)
    
    def create_vote(self, voter_answer: str):
        vote = Vote()
        vote.id_election = self
        vote.answer = voter_answer
        vote.save()
        return vote
    
    def set_has_voted(self, id_user: int):
        voter = ElectionVoter.get_element(id_election=self.id, id_user=id_user)
        voter.has_voted = True
        voter.save()

    def update_voted_candidacies(self, public_key: PaillierPublicKey, voted_candidacies: list):
        for candidacy in voted_candidacies:
            ciphertext = int(candidacy.received_votes)
            encrypted_received_votes = EncryptedNumber(public_key=public_key, ciphertext=ciphertext) + 1
            candidacy.received_votes = str(encrypted_received_votes.ciphertext())
            candidacy.save()

    def send_vote_to_blockchain(self):
        pass

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
    
    def get_candidacies(self):
        '''
        Obtém as candidaturas de um cargo.
        '''
        candidacies = Candidacy.objects.filter(id_election=self.id_election, id_position=self.id)
        if len(candidacies)>0:
            return [candidacy for candidacy in candidacies]
        return None

class Candidacy(models.Model):
    CANDIDACY_TYPE_CHOICES = (
        (CandidacyTypeEnum.Candidate.value, 'Candidato'),
        (CandidacyTypeEnum.ElectoralPlate.value, 'Chapa')
    )
    #tratar para que não exista número repetido por eleição
    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='candidacies', db_column='id_eleicao')
    id_position = models.ForeignKey(Position, on_delete=models.DO_NOTHING, related_name='candidacies', db_column='id_cargo')
    candidates = models.ManyToManyField(to=CustomUser, related_name='candidacies', db_table="candidacy_candidate")
    type = models.IntegerField(verbose_name="Tipo", choices=CANDIDACY_TYPE_CHOICES, db_column='tipo')
    number = models.IntegerField(verbose_name="Número", db_column='numero')
    name = models.CharField(verbose_name='Nome', max_length=100, help_text='Máximo 100 caracteres', db_column='Nome')
    description = models.CharField(verbose_name='Descrição', max_length=300, help_text='Máximo 300 caracteres', db_column='descricao')
    received_votes = models.CharField(verbose_name='Votos recebidos', max_length=300, default='', help_text='Máximo 300 caracteres', db_column='votos_recebidos')
    last_change = models.DateTimeField(verbose_name='Última alteração', auto_now=True, db_column='ultima_alteracao')

    class Meta:
        verbose_name = 'Candidatura'
        verbose_name_plural = 'Candidaturas'
        ordering = ['?']

    def save(self, *args, **kwargs):
        if not self.pk:
            public_key = self.id_election.load_public_key()
            cipher = public_key.encrypt(0)
            self.received_votes = str(cipher.ciphertext())
        super(Candidacy, self).save(*args, **kwargs)

    @staticmethod
    def get_element_by_id(id_candidacy: int):
        try:
            candidacy = Candidacy.objects.get(id=id_candidacy)
            return candidacy
        except Candidacy.DoesNotExist:
            return None
        
    @staticmethod
    def check_if_element_exists(id_election: int, id_position:int, number: int):
        return Candidacy.objects.filter(id_election=id_election, id_position=id_position, number=number).exists()
    
    @staticmethod
    def get_element(id_election: int, id_position:int, number: int):
        result = Candidacy.objects.filter(id_election=id_election, id_position=id_position, number=number)
        if len(result)>0:
            return result[0]
        else:
            return None

class ElectionVoter(models.Model):
    '''
    Representa um eleitor elígel para votar numa eleição. 
    Indica se votou.
    '''
    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='election_voters', db_column='id_eleicao')
    id_user = models.ForeignKey(CustomUser, on_delete=models.DO_NOTHING, db_column='id_autor')
    has_voted = models.BooleanField(verbose_name="Votou", default=False, db_column='votou')

    class Meta:
        verbose_name = 'Eleitor Elegível'
        verbose_name_plural = 'Eleitores Elegíveis'
        ordering = ['id']
        
    @staticmethod
    def check_if_element_exists(id_election: int, id_user: int):
        '''
        Retorna True se existir elemento com id_election e id_user informados.
        '''
        return ElectionVoter.objects.filter(id_election=id_election, id_user=id_user).exists()
    
    @staticmethod
    def get_element(id_election: int, id_user: int):
        '''
        Retorna um elemento com id_election e id_user informados, ou None se não existir.
        '''
        result = ElectionVoter.objects.filter(id_election=id_election, id_user=id_user)
        if len(result)>0:
            return result[0]
        return None

class Vote(models.Model):
    id_election = models.ForeignKey(Election, on_delete=models.DO_NOTHING, related_name='votes', db_column='id_eleicao')
    answer = models.CharField(verbose_name='Resposta', max_length=500, db_column='resposta')

class ElectionResult(models.Model):
    id_election = models.OneToOneField(Election, verbose_name='Eleição', on_delete=models.DO_NOTHING, db_column='id_eleicao')
    result = models.CharField(verbose_name='Resultado', max_length=100, db_column='resultado')
    creation = models.DateTimeField(verbose_name='Criação', auto_now=False, db_column='criacao')
    
    class Meta:
        verbose_name = 'Resultado de Eleição'
        verbose_name_plural = 'Resultados de Eleições'
        ordering = ['id']

class ElectionTransaction(models.Model):
    '''
    Referência para o registro das informações da eleição gravadas na blockchain.
    '''
    id_lection_result = models.OneToOneField(Election, verbose_name='Eleição', on_delete=models.DO_NOTHING, db_column='id_eleicao')
    id_transaction = models.CharField(verbose_name='Transação', max_length=64, db_column='id_transacao')

    class Meta:
        verbose_name = 'Transação da Eleição'
        verbose_name_plural = 'Transações das Eleições'

class ElectionResultTransaction(models.Model):
    '''
    Referência para o resultado da eleição gravado na blockchain.
    '''
    id_lection = models.OneToOneField(ElectionResult, on_delete=models.DO_NOTHING, db_column='id_resultado_eleicao')
    id_transaction = models.CharField(verbose_name='Transação', max_length=64, db_column='id_transacao')

    class Meta:
        verbose_name = 'Transação do Resultado de Eleição'
        verbose_name_plural = 'Transações de Resultados de Eleições'