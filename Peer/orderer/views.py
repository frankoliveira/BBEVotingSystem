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

import json, time
from hashlib import sha256
import requests

from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view

@api_view(['POST']) 
def pending_transaction(request, format=None):
    #remote_ip = get_remote_ip(request)
    port = request.data["port"]
    remote_peer = None
    
    try:
        remote_peer = Peer.objects.get(port=port) #usar ip em produção
    except Peer.DoesNotExist:
        return Response(data='Você não tem permissão', status=status.HTTP_400_BAD_REQUEST)
        
    if not remote_peer.is_publishing_node:
        input = request.data['input']
        id = sha256(input.encode()).hexdigest()
        pending = PendingTransaction()
        pending.id = id
        pending.input = input
        pending.timestamp = datetime.now()
        pending.signature = 'assinatura'
        pending.confirmed = False
        pending.save()
        pending_transaction_serializer = PendingTransactionSerializer(instance=pending)
        Orderer.broadcast_pending_transaction(pending_transaction_serializer.data)
        return Response(pending_transaction_serializer.data, status=status.HTTP_201_CREATED)
    else: 
        pending_transaction_serializer = PendingTransactionSerializer(data=request.data["transaction"])

        if pending_transaction_serializer.is_valid():
            pending_transaction_serializer.save()
            return Response("ok", status=status.HTTP_201_CREATED)
        
        return Response(pending_transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#inicia o consenso
@api_view(['GET']) 
def create_consensus_block(request, format=None):
    '''
    Essa lógica será executada de alguma forma pelo líder
    Aqui se inicia a proposta de bloco pelo líder
    '''
    if request.method == 'GET':
        try:
            block_serializer_data = Orderer.propose_block()
            if block_serializer_data:
                return Response(data=block_serializer_data, status=status.HTTP_201_CREATED)
            return Response(data='Não há transações pendentes', status=status.HTTP_200_OK)
        except Exception as ex:
            return Response(data=f"Erro na solicitação ccb:{ex}", status=status.HTTP_400_BAD_REQUEST)
        
#prepare/
@api_view(['POST'])
def prepare(request, format=None):
    """
    Recebe o novo bloco na fase de prepare
    """
    if request.method == 'POST':
        port = request.data["port"] #usando porta para diferenciar entre peers da mesma maquina
        remote_peer = None

        try:
            remote_peer = Peer.objects.get(port=port) #usar ip em produção
        except Peer.DoesNotExist:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)

        if remote_peer.is_publishing_node:
            block_serializer = BlockSerializer(data=request.data["block"])
            if block_serializer.is_valid():
                #fazer validação
                Orderer.get_instance().consensus_block_dict = block_serializer.data
                '''
                commit_dict = {
                    "commit": True
                }
                '''
                Orderer.commit(commit=True)
                return Response(data='ok', status=status.HTTP_200_OK)
            return Response(block_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
                Orderer.get_instance().consensus_positive_commits += 1
            elif received_commit == False:
                Orderer.get_instance().consensus_positive_commits += 1
            return Response(data='ok', status=status.HTTP_200_OK)
        else:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def decide(request, format=None):
    if request.method == 'GET':
        time.sleep(5)
        Orderer.get_instance().decide()
        return Response(data='ok', status=status.HTTP_200_OK)