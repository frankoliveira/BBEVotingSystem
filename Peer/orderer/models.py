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
        self.peer_port = 8000
        self.transactions_per_block = 2
        self.consensus_block_dict = None
        self.consensus_received_commits = 0
        self.consensus_is_achieved = False
        self.rsa_private_key = CustomRSA.load_pem_private_key_from_file(path='rsa_keys/private_key.pem')

    @classmethod
    def get_instance(self):
        if self.instance == None:
            self.instance = self()
        return self.instance
    
    @staticmethod
    def get_remote_ip(request):
        ip = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def broadcast_pending_transaction(transction_dict: dict) -> None:
        message = {
            "port": Orderer.get_instance().peer_port,
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
        unconfirmed_transactions = Transaction.get_unconfirmed_transactions(max_quantity=Orderer.get_instance().transactions_per_block)

        if unconfirmed_transactions!=None:
            transactions_serializer =  TransactionSerializer(instance=unconfirmed_transactions, many=True)

            block = Block()
            block.peer = str(Orderer.get_instance().peer_port)
            block.timestamp = datetime.now()
            block.merkle_root = 'merkle'
            block.previous_hash = Block.objects.last().hash()
            block.transactions = json.dumps(transactions_serializer.data)
            return block
        return None
    
    @staticmethod
    def propose_block():
        '''
        Líder inicia a eleição ao propor bloco
        '''
        Orderer.get_instance().consensus_block_dict = None
        Orderer.get_instance().consensus_received_commits = 0
        Orderer.get_instance().consensus_is_achieved = False
        new_block = Orderer.create_consensus_block()

        if new_block:
            block_serializer = BlockSerializer(instance=new_block)
            Orderer.get_instance().consensus_block_dict = block_serializer.data
            Orderer.send_prepare(block_dict=block_serializer.data)
            Orderer.send_commit()
            return block_serializer.data
        return None
    
    @staticmethod
    def send_prepare(block_dict):
        '''
        Líder anuncia novo bloco para os peers
        '''
        message = {
            "port": Orderer.get_instance().peer_port,
            "block": block_dict
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/prepare/'
                requests.post(url=url,
                              json=message)
            except Exception as ex:
                print(f"erro ao enviar prepare para o peer {peer.host}:{peer.port}")
        
        time.sleep(1)

    @staticmethod
    def send_commit():
        '''
        Envia o commit com o bloco
        '''
        message = {
            "port": Orderer.get_instance().peer_port,
            "block":  Orderer.get_instance().consensus_block_dict
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/commit/'
                requests.post(url=url,
                              json=message)
            except Exception as ex:
                print(f"erro ao enviar commit para o peer {peer.host}:{peer.port}")

    @staticmethod
    def decide():
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

            Orderer.get_instance().consensus_block_dict = None
            Orderer.get_instance().consensus_received_commits = 0
            Orderer.get_instance().consensus_is_achieved = True
