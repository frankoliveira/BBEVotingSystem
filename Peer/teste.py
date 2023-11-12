import requests, json

pending_transaction = {
    "port": "8080",
    "input": "voto3",
    "teste": {
        "transacoes": [1, 2, 3],
        "assinatura": "fsgasgfh"
    }
}

url = 'http://127.0.0.1:8000/pending-transactions/'
#requests.post(url=url, json=pending_transaction)



import json
from hashlib import sha256 
from datetime import datetime

class Block():

    def __init__(self, id, peer, timestamp, merkle_root, previous_hash, transactions):
        self.id = id
        self.peer = peer
        self.timestamp = timestamp
        self.merkle_root = merkle_root
        self.previous_hash = previous_hash
        self.transactions = transactions
    
    def block_header_as_dict(self):
        #block = vars(self)
        return {
            "id":    self.id,
            'peer': self.peer,
            'timestamp': self.timestamp.strftime("%d/%m/%Y, %H:%M:%S"),
            'merkle_root': self.merkle_root,
            'previous_hash': self.previous_hash
        }
        
    def hash(self):
        block_string = json.dumps(self.block_header_as_dict(), sort_keys=True)
        block_hash = sha256(block_string.encode()).hexdigest()
        return block_hash

block = Block(0, 'peer', datetime.now(), 'merkle', 'asgaadfh', '[ "tran" ]')

print(block.block_header_as_dict())

block_str = json.dumps(block.block_header_as_dict())
print(type(block.block_header_as_dict()))
print(type(block_str))
print(block_str)
print(json.loads(block_str))