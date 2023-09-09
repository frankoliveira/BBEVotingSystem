from messenger import MessageConfiguration, MessageSender
from models import Orderer
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
    login='peer1',
    password='123456',
    sender_exchange='transactions',
    sender_routing_key='transactions',
    receiver_queue='transactions',
    receiver_exchange='transactions',
    receiver_routing_key='transactions'
)

class TransactionList(APIView):
    def post(self, request, format=None):
        try:
            transaction_data = str(request.data)
            transaction = Orderer.create_transaction(transaction_data)
            transaction_str = json.dumps(transaction, sort_keys=True)

            MessageSender.send(configuration=message_config,
                               data=transaction_str)
            return Response(data=f'Transacao criada com id: {transaction.id}', status=status.HTTP_201_CREATED)
        except:
            return Response("Erro ao adicionar transação.", status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def create_transaction(request, format=None):
    """
    Create a transaction
    """

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
        
    return Response("Erro ao criar bloco.", status=status.HTTP_400_BAD_REQUEST)
