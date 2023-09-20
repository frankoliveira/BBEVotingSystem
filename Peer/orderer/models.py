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
from transaction.models import PendingTransaction, TransactionBlock
from peer.models import Peer

#Serializers
from block.serializers import BlockSerializer
from transaction.serializers import PendingTransactionSerializer

class Orderer():
    instance = None
    peer_port = 8000
    transactions_per_block = 1
    
    consensus_block_dict = None
    consensus_received_commits = 0
    consensus_is_achieved = False

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
                requests.post(url=url, json=message)
            except Exception as ex:
                print(f"erro broadcast_pending_transaction: {ex}")

    @staticmethod
    def create_consensus_block() -> Block:
        try:
            pending_transactions = None
            pending_transactions = PendingTransaction.objects.filter(confirmed=False)
            oldest_pending_transactions = None
            if pending_transactions:
                oldest_pending_transactions = pending_transactions.order_by("timestamp")[0]

            if oldest_pending_transactions:
                pending_transaction_serializer = PendingTransactionSerializer(instance=oldest_pending_transactions)
                
                block = Block()
                block.peer = str(Orderer.get_instance().peer_port)
                block.timestamp = datetime.now()
                block.merkle_root = 'merkle'
                block.previous_hash = Block.objects.last().hash()
                block.transactions = json.dumps([pending_transaction_serializer.data])

                return block
            return None
        except Exception as ex:
            pass
    
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
            print(f'bloco original: {new_block.transactions}')
            print(f'bloco serializado: {block_serializer.data}')
            Orderer.get_instance().consensus_block_dict = block_serializer.data
            Orderer.send_prepare(block_dict=block_serializer.data)
            Orderer.send_commit(commit=True)

            #Orderer.decide()
            #havia aqui a requisição http decide

            return block_serializer.data
        return None
    
    @staticmethod
    def send_prepare(block_dict):
        '''
        Líder anuncia novo bloco para os peers
        '''
        message = {
            "port": Orderer.get_instance().peer_port,
            "prepare": {
                "block": block_dict
            }
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/prepare/'
                requests.post(url=url,
                              json=message)
            except Exception as ex:
                print(f"erro prepare: {ex}")
        
        print("prepare func ok")

    @staticmethod
    def send_commit(commit):
        '''
        Todos os peers enviam resultado da análise pós-prepare, positiva ou negativa
        '''
        message = {
            "port": Orderer.get_instance().peer_port,
            "commit": commit
        }

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/commit/'
                requests.post(url=url,
                              json=message)
            except Exception as ex:
                print(f"erro commit: {ex}")
        
        print('commit func ok')

    @staticmethod
    def decide():
        block = None
        if Orderer.get_instance().consensus_received_commits > 0:
            block_serializer = BlockSerializer(data=Orderer.get_instance().consensus_block_dict)

            if block_serializer.is_valid():
                block: Block = block_serializer.save()

                #confirmação das transações pendentes
                transactions_list: list = json.loads(block.transactions)

                for i in range(len(transactions_list)):
                    transaction_dict = transactions_list[i]
                    transaction = PendingTransaction.objects.get(pk=transaction_dict["id"])
                    transaction.confirmed = True
                    transaction.save()

                    #referência entre transação e bloco
                    transaction_block = TransactionBlock()
                    transaction_block.id_transaction = transaction.id
                    transaction_block.id_block = block.id
                    transaction_block.position = i
                    transaction_block.timestamp = datetime.now()
                    transaction_block.save()

                print("bloco criado pelo consenso")

            Orderer.get_instance().consensus_block_dict = None
            Orderer.get_instance().consensus_received_commits = 0
            Orderer.get_instance().consensus_is_achieved = True

        return block
