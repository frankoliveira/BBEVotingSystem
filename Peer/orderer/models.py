import json, requests
from hashlib import sha256
from datetime import datetime
from typing import Union

#Models
from block.models import Block
from transaction.models import PendingTransaction
from peer.models import Peer


#Serializers
from block.serializers import BlockSerializer
from transaction.serializers import PendingTransactionSerializer

class Orderer():
    instance = None
    peer_port = 8000
    transactions_per_block = 1
    
    consensus_block_dict = None
    consensus_positive_commits = 0
    consensus_negative_commits = 0
    consensus_decision = False

    def __init__(self) -> None:
        pass

    @classmethod
    def get_instance(self):
        if self.instance == None:
            self.instance = self()
        return self.instance
    
    @staticmethod
    def mount_transaction_message(data: str) -> dict:
        id = sha256(data.encode()).hexdigest()
        timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        transaction = {"id": id, "timestamp": timestamp, "data": data}
        return transaction
    
    @staticmethod
    def get_remote_ip(request):
        ip = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @classmethod
    def get_instance(self):
        if self.instance == None:
            self.instance = self()
        return self.instance
    
    @staticmethod
    def broadcast_pending_transaction(pending_transction_dict):
        message = {
            "port": Orderer.get_instance().peer_port,
            "transaction": pending_transction_dict
        }


        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/pending-transactions/'
                requests.post(url=url, json=pending_transction_dict)
            except Exception as ex:
                print(f"erro broadcast_pending_transaction: {ex}")

    @staticmethod
    def create_consensus_block() -> Block:
        try:
            pending_transaction = PendingTransaction.objects.last()

            if pending_transaction:
                pending_transaction_serializer = PendingTransactionSerializer(pending_transaction)

                block = Block()
                block.peer = str(Orderer.get_instance().peer_port)
                block.timestamp = datetime.now()
                block.merkle_root = ''
                block.previous_hash = Block.objects.last().hash()
                block.transactions = {"transactions":[pending_transaction_serializer.data]}
                return block
            return None
        except Exception as ex:
            pass
    
    @staticmethod
    def propose_block():
        '''
        Líder inicia a eleição ao propor bloco
        '''
        new_block = Orderer.create_consensus_block()
        block_serializer = None
        
        if new_block:
            block_serializer = BlockSerializer(new_block)
            Orderer.get_instance().consensus_block_dict = block_serializer.data
            Orderer.prepare(block_dict=block_serializer.data)
            Orderer.commit(commit_dict="AQUI VEM O DICT")

        return block_serializer.data
    
    @staticmethod
    def prepare(block_dict):
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
                print(f"erro prepare: {ex}")

    @staticmethod
    def commit(commit_dict):
        '''
        Todos os peers enviam resultado da análise pós-prepare, positiva ou negativa
        '''
        message = {
            "port": Orderer.get_instance().peer_port,
            "commit": commit_dict
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/commit/'
                requests.post(url=url,
                              json=message)
            except Exception as ex:
                print(f"erro commit: {ex}")

    @staticmethod
    def decide():
        if Orderer.get_instance().consensus_positive_commits > 1:
            block_serializer = BlockSerializer(Orderer.get_instance().consensus_block_dict)
            if block_serializer.is_valid():
                block: Block = block_serializer.save()
                print(json.loads(Block.transactions))
        
        Orderer.get_instance().consensus_block_dict = None
        Orderer.get_instance().consensus_positive_commits = 0
        Orderer.get_instance().consensus_negative_commits = 0
        Orderer.get_instance().consensus_decision = False
