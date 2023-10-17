import json, requests
from hashlib import sha256
from datetime import datetime
from typing import Union
import time
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import io

#Models
from block.models import Block
from transaction.models import Transaction, TransactionBlock
from peer.models import Peer
from security.models import CustomRSA

#Serializers
from block.serializers import BlockSerializer
from transaction.serializers import TransactionSerializer

class Orderer():
    instance = None
    
    def __init__(self) -> None:
        self.peer_id = '127.0.0.1:8000'
        self.transactions_per_block = 2
        self.consensus_leader_id = '127.0.0.1:8000'
        
        self.consensus_view = 1
        self.consensus_block_dict = None
        self.consensus_block_hash = None
        self.consensus_received_prepares = 0
        self.consensus_sent_commit = False
        self.consensus_received_commits = 0
        self.consensus_is_achieved = False
        #self.rsa_private_key = CustomRSA.load_pem_private_key_from_file(path='rsa_keys/private_key.pem')

    @classmethod
    def get_instance(self):
        if self.instance == None:
            self.instance = self()
        return self.instance
    
    def reset_consensus_values(self):
        '''
        not static
        '''
        self.consensus_block_dict = None
        self.consensus_block_hash = None
        self.consensus_received_prepares = 0
        self.consensus_sent_commit = False
        self.consensus_received_commits = 0
        self.consensus_is_achieved = False
    
    @staticmethod
    def get_remote_ip(request):
        '''
        static
        '''
        ip = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:

            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def check_pre_prepare_hash(block: dict, block_hash: str) -> bool:
        '''
        static
        '''
        return True
    
    @staticmethod
    def broadcast_pending_transaction(transction_dict: dict) -> None:
        '''
        static
        '''
        message = {
            "peer_id": Orderer.get_instance().peer_id,
            "transaction": transction_dict
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/pending-transactions/'
                requests.post(url=url, json=message)
            except Exception as ex:
                print(f"erro broadcast_pending_transaction: {ex}")

    @staticmethod
    def create_consensus_block() -> Block:
        '''
        static
        '''
        orderer = Orderer.get_instance()
        unconfirmed_transactions = Transaction.get_unconfirmed_transactions(max_quantity=orderer.transactions_per_block)

        if unconfirmed_transactions!=None:
            transactions_serializer =  TransactionSerializer(instance=unconfirmed_transactions, many=True)
            block = Block()
            block.peer = orderer.peer_id
            block.timestamp = datetime.now()
            block.merkle_root = 'merkle'
            block.previous_hash = Block.objects.last().hash()
            block.transactions = json.dumps(transactions_serializer.data)
            return block
        return None
    
    @staticmethod
    def propose_block():
        '''
        static - Líder inicia a eleição ao propor bloco
        '''
        orderer = Orderer.get_instance()
        orderer.reset_consensus_values()
        new_block = Orderer.create_consensus_block()

        if new_block:
            block_serializer = BlockSerializer(instance=new_block)
            orderer.consensus_block_dict = block_serializer.data
            orderer.consensus_block_hash = "hash"
            Orderer.send_pre_prepare(block_dict=block_serializer.data)
            #Orderer.send_prepare()
            #Orderer.send_commit()
            return block_serializer.data
        return None
    
    @staticmethod
    def send_pre_prepare(block_dict):
        '''
        static - Líder anuncia novo bloco para os peers
        '''
        #obs:
        #no artigo temos: v:view, n:client request order number, m: message, d: hash digest of message m
        orderer = Orderer.get_instance()
        message = {
            "peer_id": orderer.peer_id, #usando para identificação
            "view": orderer.consensus_view, #v: rodada atual, um número consecutivo
            "block": block_dict, #m: mensagem
            "block_hash": "hash", #d: hash da mensagem
            "block_hash_signature": "signature" #assinatura
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/pre-prepare/'
                requests.post(url=url,
                              json=message)
            except Exception as ex:
                print(f"erro ao enviar pré-prepare para o peer {peer.host}:{peer.port}")

    @staticmethod
    def send_prepare():
        '''
        static
        '''
        orderer = Orderer.get_instance()
        message = {
            "peer_id": orderer.peer_id,
            "view": orderer.consensus_view,
            #"n": 1,
            "block_hash": orderer.consensus_block_hash
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/prepare/'
                requests.post(url=url,
                              json=message)
            except Exception as ex:
                print(f"erro ao enviar prepare para o peer {peer.host}:{peer.port}")

    @staticmethod
    def send_commit():
        '''
        static
        '''
        orderer = Orderer.get_instance()
        message = {
            "peer_id": orderer.peer_id,
            "view": orderer.consensus_view,
            "block_hash": orderer.consensus_block_hash
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/commit/'
                requests.post(url=url,
                              json=message)
            except Exception as ex:
                print(f"erro ao enviar commit para o peer {peer.host}:{peer.port}")
        orderer.consensus_sent_commit = True

    @staticmethod
    def decide():
        '''
        static
        '''
        if Orderer.get_instance().consensus_received_commits > 0:
            block_serializer = BlockSerializer(data=Orderer.get_instance().consensus_block_dict)

            if block_serializer.is_valid():
                block: Block = block_serializer.save()

                #confirmação das transações pendentes
                transactions_list: list = json.loads(block.transactions)

                for i in range(len(transactions_list)):
                    transaction_dict = transactions_list[i]
                    transaction = Transaction.objects.get(pk=transaction_dict["id"])
                    transaction.confirmed = True
                    transaction.save()

                    #referência entre transação e bloco
                    transaction_block = TransactionBlock()
                    transaction_block.id_transaction = transaction.id
                    transaction_block.id_block = block.id
                    transaction_block.position = i
                    transaction_block.timestamp = datetime.now()
                    transaction_block.save()

            #Orderer.get_instance().consensus_block_dict = None
            #Orderer.get_instance().consensus_received_commits = 0
            Orderer.get_instance().consensus_is_achieved = True
