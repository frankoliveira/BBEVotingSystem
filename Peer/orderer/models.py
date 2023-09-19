import json
from hashlib import sha256
from datetime import datetime

from django.db import models

# Create your models here.
class Orderer():
    instance = None
    peer_port = 8000
    transaction_per_block = 1
    #block serialized
    consensus_new_block = None
    consensus_commits = 0
    consensus_new_block_aproved = False

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
    