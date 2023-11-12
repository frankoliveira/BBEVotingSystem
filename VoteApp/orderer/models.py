import json, requests
from hashlib import sha256
from datetime import datetime
from typing import Union
import time
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import io

#Models
from peer.models import Peer
#from security.CustomRSA import CustomRSA

#Serializers


class Orderer():
    instance = None
    
    def __init__(self) -> None:
        self.peer_id = '127.0.0.1:8080'
        self.consensus_leader_id = '127.0.0.1:8000'

    @classmethod
    def get_instance(self):
        if self.instance == None:
            self.instance = self()
        return self.instance
    
    @staticmethod
    def get_remote_ip(request):
        '''
        static
        '''
        ip = None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:

            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    
    @staticmethod
    def create_transaction(input: str) -> None:
        '''
        static
        '''
        message = {
            "peer_id": Orderer.get_instance().peer_id,
            "input": input
        }

        try:
            url = f'http://127.0.0.1:8000/pending-transactions/'
            response = requests.post(url=url, json=message)
            return response.json()['id']
        except Exception as ex:
            print(f"erro ao criar transação: {ex}")
            return None
