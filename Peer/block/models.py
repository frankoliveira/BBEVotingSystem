from django.db import models
from hashlib import sha256
import json
from datetime import datetime

class Block(models.Model):
    #editable=False: the field will not be displayed in the admin or any other ModelForm. They are also skipped during model validation.
    peer = models.CharField('Peer', max_length=100, db_column='peer') #nó responsável pela criação do bloco
    timestamp = models.DateTimeField('Timestamp', auto_now=False, db_column='timestamp') #cria a hora sozinho a cada save()
    merkle_root = models.CharField('Merkle Root', max_length=64, db_column='merkle_root') #equivale ao hash da raiz da Mekle Tree
    previous_hash = models.CharField('Previous Hash', max_length=64, db_column='previous_hash')
    transactions = models.CharField('Transactions', max_length=100, db_column='transactions')
    
    class Meta:
        verbose_name = 'Block'
        verbose_name_plural = 'Blocks'
        ordering = ['id']

    def __str__(self) -> str:
        return str(self.pk)
    
    def as_dict(self):
        #block = vars(self)
        return {
            'id': self.id,
            'peer': self.peer,
            'timestamp': self.timestamp.strftime("%d/%m/%Y, %H:%M:%S"),
            'merkle_root': self.merkle_root,
            'previous_hash': self.previous_hash
        }
        
    def hash(self):
        block_string = json.dumps(self.as_dict(), sort_keys=True)
        block_hash = sha256(block_string.encode()).hexdigest()
        return block_hash
