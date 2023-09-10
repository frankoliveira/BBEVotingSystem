from .messenger import MessageConfiguration, MessageSender, MessageReceiver
from blockchain.models import Blockchain
#Models
from .models import Orderer
from transaction.models import Transaction

#Serializers
from transaction.serializers import TransactionSerializer

import json
from hashlib import sha256

from django.shortcuts import render
from blockchain.models import Blockchain
from block.serializers import BlockSerializer

#function based views
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view

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
        except Exception as ex:
                return Response(data=f"Erro na solicitação:{ex}", status=status.HTTP_400_BAD_REQUEST)


"""
@api_view(['POST'])
def create_transaction(request, format=None):
    '''
    Create a transaction
    '''

    if request.method == 'POST':

        if request.data:  
            new_block = Blockchain.create_block(
                                                peer = 'peer_1',
                                                version = '1.0.0',
                                                timestamp = datetime.now(), 
                                                merkle_root = 'merkle_root', 
                                                previous_hash = Blockchain.get_last_block().hash(),
                                                transactions = str(request.data)
                                                )
            if new_block != None:
                serializer = BlockSerializer(new_block)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    return Response('Erro ao criar bloco.', status=status.HTTP_400_BAD_REQUEST)
"""