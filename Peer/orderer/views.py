#from .messenger import MessageConfiguration, MessageSender, MessageReceiver

#Models
from .models import Orderer
from transaction.models import PendingTransaction, TransactionBlock
from block.models import Block
from blockchain.models import Blockchain
from peer.models import Peer

#Serializers
from transaction.serializers import PendingTransactionSerializer, TransactionBlockSerializer
from block.serializers import BlockSerializer

import json
from hashlib import sha256
import requests

from django.shortcuts import render

#function based views
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view

class PendingTransactionList(APIView):
    '''
    Add a transaction to the pending transactions queue.
    '''
    
    def broadcast_pending_transaction(self, pending_transaction):
        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/pending-transactions/'
                requests.post(url=url,
                              data=pending_transaction)
            except Exception as ex:
                print(f"erro broadcast_pending_transaction: {ex}")

    def post(self, request, format=None):
        #remote_ip = get_remote_ip(request)
        _port = request.data["port"] #usando porta para diferenciar entre peers da mesma maquina
        remote_peer = None

        #return Response(port, status=status.HTTP_201_CREATED)
    
        try:
            remote_peer = Peer.objects.get(port=_port) #usar ip em produção
        except Peer.DoesNotExist:
            return Response(data='Você não tem permissão', status=status.HTTP_400_BAD_REQUEST)
        
        if not remote_peer.is_publishing_node: #se foi enviado pelo app
            input = request.data['input']
            id = sha256(input.encode()).hexdigest()

            pending = PendingTransaction()
            pending.id = id
            pending.input = input
            pending.timestamp = datetime.now()
            pending.signature = ''
            pending.confirmed = False

            pending.save()
            serializer = PendingTransactionSerializer(instance=pending)
            #self.broadcast_pending_transaction(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else: 
            serializer = PendingTransactionSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response("ok", status=status.HTTP_201_CREATED)
        
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Consensus():
    '''
    Mine a block
    '''
    def __init__(self) -> None:
        pass

    @classmethod
    def get_instance(self):
        if self.instance == None:
            self.instance = self()
        return self.instance

    @staticmethod
    def create_consensus_block() -> Block:
        try:
            #cria bloco com uma transação
            pending_transaction = PendingTransaction.objects.last()

            if pending_transaction:
                pending_transaction_serializer = PendingTransactionSerializer(pending_transaction)

                block = Block()
                block.peer = str(Orderer.get_instance().peer_port)
                block.timestamp = datetime.now()
                block.merkle_root = ''
                block.previous_hash = Block.objects.last().hash()
                block.transactions = {"transactions": [pending_transaction_serializer.data] }
                return block
                
            return None
        except Exception as ex:
            pass
    
    @staticmethod
    def prepare(block_json):
        '''
        Anuncia novo bloco para os peers
        '''

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/prepare/'
                requests.post(url=url,
                              data=block_json)
            except Exception as ex:
                print(f"erro prepare: {ex}")

    @staticmethod
    def commit(commit_json):
        '''
        Envia resultado da análise, se foi positiva ou negativa
        '''

        peers = Peer.objects.filter(is_publishing_node=True)
        for peer in peers:
            try:
                url = f'http://{peer.host}:{peer.port}/commit/'
                requests.post(url=url,
                              data=commit_json)
            except Exception as ex:
                print(f"erro commit: {ex}")

    @staticmethod
    def decide():
        pass

#inicia o consenso
@api_view(['POST']) 
def create_consensus_block(request, format=None):
    if request.method == 'POST':
        try:
            new_block = Consensus.create_consensus_block()
            if new_block:
                block_serializer = BlockSerializer(new_block)

                #cópia local do bloco proposto na versão dict/json
                # Outros peers salvam o bloco do mesmo modo 
                Consensus.get_instance().consensus_new_block = block_serializer.data
                #Consensus.prepare(block_json=block_serializer.data)

                return Response(data=block_serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(data="Não há transação pendente", status=status.HTTP_201_CREATED)
        except Exception as ex:
            return Response(data=f"Erro na solicitação:{ex}", status=status.HTTP_400_BAD_REQUEST)
        
#prepare/
@api_view(['POST'])
def prepare(request, format=None):
    """
    Recebe o novo bloco na fase de prepare
    """
    if request.method == 'POST':
        _port = request.data["port"] #usando porta para diferenciar entre peers da mesma maquina
        remote_peer = None

        try:
            remote_peer = Peer.objects.get(port=_port) #usar ip em produção
        except Peer.DoesNotExist:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)

        if remote_peer.is_publishing_node:
            block_serializer = BlockSerializer(data=request.data["block"])
            if block_serializer.is_valid():
                #fazer validação
                """
                block = Block()
                block.peer = block_serializer.data['peer']
                block.timestamp = block_serializer.data['timestamp']
                block.merkle_root = block_serializer.data['merkle_root']
                block.previous_hash = block_serializer.data['previous_hash']
                block.transactions = block_serializer.data['transactions']
                Orderer.get_instance().consensus_new_block = block
                """
                Orderer.get_instance().consensus_new_block = block_serializer.data
                commit_json = {
                    "port": Orderer.get_instance().peer_port,
                    "commit": True
                }

                Consensus.commit(commit_json=commit_json)
        else:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)
        
#commit/
@api_view(['POST'])
def commit(request, format=None):
    '''
    Recebe resultado dos demais peers
    '''
    if request.method == 'POST':
        port = request.data["port"] #usando porta para diferenciar entre peers da mesma maquina
        received_commit = False
        received_commit = request.data["commit"]
        remote_peer = None

        try:
            remote_peer = Peer.objects.get(port=port) #usar ip em produção
        except Peer.DoesNotExist:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)
        
        if remote_peer.is_publishing_node:
            if received_commit == True:
                Orderer.get_instance().consensus_commits += 1

            if Orderer.get_instance().consensus_commits >= 2 and Orderer.get_instance().consensus_new_block_aproved==False:
                Orderer.get_instance().consensus_new_block_aproved==True
                #cria bloco
                #cria transações do bloco
                pass
        else:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)














"""
message_config = MessageConfiguration(
    host='127.0.0.1',
    port=5672,
    socket_timeout=1,
    login='guest',
    password='guest',
    sender_exchange='transactions_exchange',
    sender_routing_key='transactions_routing',

    receiver_queue='transactions_queue',
    receiver_exchange='transactions_exchange',
    receiver_routing_key='transactions_routing'
)

class PendingTransactionList(APIView):
    '''
    Add a transaction to the pending transactions queue.
    '''
    def post(self, request, format=None):
        try:
            data = request.data['transaction']
            transaction = Orderer.mount_transaction_message(data)
            transaction_str = json.dumps(transaction, sort_keys=True)
            MessageSender.send_transaction(configuration=message_config, data=transaction_str)
            return Response(data=f'Transação criada. ID:{transaction["id"]}', status=status.HTTP_201_CREATED)

        except Exception as ex:
            return Response(data=f"Erro na solicitação:{ex}", status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, format=None):
        try:
            num_transactions = 0
            num_transactions = MessageReceiver.get_pending_transactions(configuration=message_config)
            return Response(data=f'Transações pendentes: {num_transactions}')
        
        except Exception as ex:
            return Response(data=f"Erro na solicitação:{ex}", status=status.HTTP_400_BAD_REQUEST)
        
class ConfirmedTransactionDetail(APIView):
    '''
    Confirmed transactions.
    '''

    def get_object(self, pk):
        try:
            return Transaction.objects.get(pk=pk)
        except Transaction.DoesNotExist:
            raise Http404
        
    def get(self, request, pk, format=None):
        transaction = self.get_object(pk)
        serializer = TransactionSerializer(transaction)
        return Response(data=serializer.data)

"""
        
"""
class BlockMining(APIView):
    '''
    Mine a block
    '''
    transaction_per_block = 1

    def get(self, request, format=None):
        try:
            transaction = MessageReceiver.consume_transaction(configuration=message_config)
            if transaction:
                new_block = Blockchain.create_block(peer = 'peer_1',
                                                    timestamp = datetime.now(), 
                                                    merkle_root = 'root', 
                                                    previous_hash = Blockchain.get_last_block().hash(),
                                                    transactions = transaction
                                                    )

                serializer = BlockSerializer(new_block)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(data="Não há transação pendente", status=status.HTTP_201_CREATED)
        except Exception as ex:
                return Response(data=f"Erro na solicitação:{ex}", status=status.HTTP_400_BAD_REQUEST)
"""
