import json, requests, base64
from hashlib import sha256
from datetime import datetime
from typing import Union
import time
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
import io, os

#Models
from peer.models import Peer
from security.CustomRSA import CustomRSA
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey

#Serializers

class Orderer():
    instance = None
    
    def __init__(self, peer_number:int, peer_private_key:RSAPrivateKey) -> None:
        self.peer_number = peer_number
        self.peer_private_key: RSAPrivateKey = peer_private_key

    @classmethod
    def get_instance(self):
        if self.instance == None:
            config_values = Orderer.get_config_from_json("./appsettings.json")
            self.instance = self(peer_number=config_values["peer_number"], 
                                 peer_private_key=CustomRSA.load_pem_private_key_from_file('rsa_keys/private_key.pem'))
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
    def get_config_from_json(config_path: str) -> dict:
        if not os.path.exists(config_path):
            return None
        file = open(config_path, 'r')
        config = json.load(file)
        file.close()
        return config

    @staticmethod
    def create_transaction(input: str) -> None:
        '''
        static
        '''
        orderer = Orderer.get_instance()

        bytes_input = bytes = input.encode('utf-8')
        sign: bytes = CustomRSA.sign(private_key=orderer.peer_private_key, message=bytes_input)
        signature = base64.b64encode(sign).decode('utf-8')
        print(signature)
        message = {
            "peer_number": orderer.peer_number,
            "origin": orderer.peer_number,
            "input": input,
            "signature": signature
        }
        #peers = Peer.objects.filter(is_publishing_node=True, authorized=True).exclude(number=orderer.peer_number)
        try:
            url = f'http://127.0.0.1:8000/pending-transactions/'
            response = requests.post(url=url, json=message)
            return response.json()['id']
        except Exception as ex:
            print(f"erro ao criar transação: {ex}")
            return None
