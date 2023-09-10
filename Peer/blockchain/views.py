from block.models import Block
from blockchain.models import Blockchain
from block.serializers import BlockSerializer

#function based views
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
from rest_framework.decorators import api_view

"""
#class based view
class BlockList(APIView):
    def get(self, request, format=None):
        blocks = Block.objects.all()
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = BlockSerializer(data=request.data)
        if serializer.is_valid():
            # datetime(year, month, day, hour, minute, second, microsecond)
            #date = datetime(2022, 12, 28, 23, 55, 59, 342380)
            #serializer.save(timestamp = date)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""


@api_view(['POST'])
def blockchain_list(request, format=None):
    """
    Create a blockchain by genesis block.
    """
    if request.method == 'POST':
        last_block = Blockchain.get_last_block()

        if last_block == None:
            genesis_block = Blockchain.create_genesis_block()
            serializer = BlockSerializer(genesis_block)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response("Genesis block not created", status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET','POST'])
def blockchain_block_list(request, format=None):
    """
    List all blocks or create a new.
    """
    if request.method == 'GET':
        blocks = Block.objects.all()
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = BlockSerializer(data=request.data)
        if serializer.is_valid():  
            new_block = Blockchain.create_block(
                                                peer = serializer.data['peer'],
                                                timestamp = serializer.data['timestamp'], 
                                                merkle_root = serializer.data['merkle_root'], 
                                                previous_hash = serializer.data['previous_hash'],
                                                transactions = serializer.data['transactions'] 
                                                )
            serializer = BlockSerializer(new_block)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response("Block not created", status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def blockchain_block_detail(request, pk, format=None):
    """
    Retrieve a block by id.
    """
    try:
        block = Block.objects.get(pk=pk)
    except Block.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = BlockSerializer(block)
        return Response(serializer.data)

@api_view(['GET'])
def blockchain_validity(request, format=None):
    """
    Checks the blockchain validity.
    """
    if request.method == 'GET':
        result = Blockchain.get_chain_validity()
        return Response(f"Validity: {result}", status=status.HTTP_201_CREATED)

"""
#exemplo de como passar um valor na view
def post(self, request, format=None):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(creator=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)"""