#Models
from .models import Orderer
from transaction.models import Transaction, TransactionBlock
from block.models import Block
from blockchain.models import Blockchain
from peer.models import Peer
from security.models import CustomRSA

#Serializers
from transaction.serializers import TransactionSerializer, TransactionBlockSerializer
from block.serializers import BlockSerializer

#Other
import json, time
from hashlib import sha256
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view

@api_view(['POST']) 
def pending_transaction(request, format=None):
    '''
    Create a transaction with input from voting app
    Or receive a created transaction from a publishing node
    '''
    if request.method == 'POST':
        #remote_ip = get_remote_ip(request)
        remote_peer: Peer = Peer.get_peer_by_port(port=request.data["port"])
        
        if remote_peer==None:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)
        
        if remote_peer.is_publishing_node:
            transaction_serializer = TransactionSerializer(data=request.data["transaction"])

            if transaction_serializer.is_valid():
                transaction_serializer.save()
                return Response("ok", status=status.HTTP_201_CREATED)
            
            return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            input = request.data['input']
            id = sha256(input.encode('utf-8')).hexdigest()
            if Transaction.check_if_exist(id=id)==False and TransactionBlock.check_if_exist(id=id)==False:
                transaction = Transaction.objects.create(
                    id = id,
                    input = input,
                    timestamp = datetime.now()
                )

                transaction_serializer = TransactionSerializer(instance=transaction)
                Orderer.broadcast_pending_transaction(transaction_serializer.data)
                return Response(transaction_serializer.data, status=status.HTTP_201_CREATED)
            return Response(data='Transação inválida', status=status.HTTP_400_BAD_REQUEST)

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
    Recebe o novo bloco do Líder na fase de prepare
    """
    if request.method == 'POST':
        remote_peer: Peer = Peer.get_peer_by_port(port=request.data["port"])
        if remote_peer!=None and remote_peer.is_publishing_node:
            Orderer.get_instance().consensus_block_dict = None
            Orderer.get_instance().consensus_received_commits = 0
            Orderer.get_instance().consensus_is_achieved = False
            block_serializer = BlockSerializer(data=request.data["block"])
            
            if block_serializer.is_valid():
                #fazer validação
                Orderer.get_instance().consensus_block_dict = block_serializer.data
                Orderer.send_commit()
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
        remote_peer: Peer = Peer.get_peer_by_port(port=request.data["port"])
        if remote_peer!=None and remote_peer.is_publishing_node:
            #block_commit = request.data["block"]
            if Orderer.get_instance().consensus_is_achieved == False:
                Orderer.get_instance().consensus_received_commits += 1
                Orderer.get_instance().decide()
            return Response(data='ok', status=status.HTTP_200_OK)
        else:
            return Response(data='Peer não tem permissão', status=status.HTTP_400_BAD_REQUEST)