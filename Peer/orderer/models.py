import json
from hashlib import sha256
from datetime import datetime

from django.db import models

# Create your models here.
class Orderer():
    @staticmethod
    def mount_transaction_message(data: str) -> dict:
        id = sha256(data.encode()).hexdigest()
        timestamp = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        transaction = {"id": id, "timestamp": timestamp, "data": data}
        return transaction
    
        