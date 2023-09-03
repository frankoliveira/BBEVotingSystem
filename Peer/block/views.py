from blockchain.models import Block, Blockchain
from blockchain.serializers import BlockSerializer

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