import json
from hashlib import sha256

from django.db import models

# Create your models here.
class Orderer():
    @staticmethod
    def create_transaction(data: str) -> object:
        transaction_id = sha256(data.encode()).hexdigest()
        transaction = {"transaction": {"id": transaction_id, "data": data}}
        return transaction
            
    