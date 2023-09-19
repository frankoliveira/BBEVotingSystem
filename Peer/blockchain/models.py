from django.db import models
from hashlib import sha256
from datetime import datetime
from block.models import Block

class Blockchain:
    def __init__(self):
        pass
    
    @staticmethod
    def create_genesis_block() -> Block:
        #chain_size = Block.objects.all.count()
        genesis_block = Block(
                              peer = '8000',
                              #timestamp = datetime(2022, 12, 28, 23, 55, 59, 342380),
                              timestamp = datetime.now(),
                              merkle_root = '',
                              previous_hash = '',
                              transactions= ''
                              )
        genesis_block.save()
        return genesis_block

    @staticmethod
    def create_block(peer, timestamp, merkle_root, previous_hash, transactions) -> Block:
        last_block = Block.objects.last()
        if last_block:
            new_block = Block.objects.create(
                                             peer = peer,
                                             timestamp = timestamp,
                                             merkle_root = merkle_root, 
                                             previous_hash=last_block.hash(),
                                             transactions = transactions
                                             ) 
            return new_block
        return None

    @staticmethod
    def get_last_block() -> Block:
        return Block.objects.last()

    @staticmethod
    def get_chain_validity() -> bool:
        block_chain = Block.objects.all()
        previous_block = block_chain[0]
        block_index = 1
        
        while block_index < block_chain.count():
            block = block_chain[block_index]
            if block.previous_hash != previous_block.hash():
                return False
            previous_block = block
            block_index += 1
        
        return True

