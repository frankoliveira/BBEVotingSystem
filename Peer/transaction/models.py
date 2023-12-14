from django.db import models

class Transaction(models.Model):
    '''
    Transactions
    '''
    id = models.CharField(verbose_name='ID', primary_key=True, max_length=64, db_column='id') #hash dos atributos abaixo
    input = models.CharField(verbose_name='Data', max_length=500, db_column='input') #voto
    timestamp = models.DateTimeField(verbose_name='Timestamp', auto_now=False, db_column='timestamp') #recebimento
    confirmed = models.BooleanField(verbose_name='Confirmed', default=False, db_column='confirmed')
    origin = models.CharField(verbose_name='Origin', max_length=200, db_column='origin')
    signature = models.CharField(verbose_name='Signature', max_length=300, db_column='signature')
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['timestamp']

    def __str__(self) -> str:
        return str(self.id)
    
    @staticmethod
    def check_if_exist(id: str) -> bool:
        try:
            peer = Transaction.objects.get(id=id)
            return True
        except Transaction.DoesNotExist:
            return False
    
    @staticmethod
    def get_unconfirmed_transactions(max_quantity: int):
        unconfirmed_transactions = Transaction.objects.filter(confirmed=False)
        
        if unconfirmed_transactions:
            ordered_transactions = unconfirmed_transactions.order_by("timestamp")
            total = len(ordered_transactions)
            quantity_to_return = total if total < max_quantity else max_quantity
            return ordered_transactions[:quantity_to_return]
        else:
            return None
        
    @staticmethod
    def get_element_by_id(id: int):
        try:
            transaction = Transaction.objects.get(id=id)
            return transaction
        except Transaction.DoesNotExist:
            return None
    
class TransactionBlock(models.Model):
    '''
    Confirmed transaction reference, the data is stored inside the block
    '''
    id_transaction = models.CharField(verbose_name='ID', primary_key=True, max_length=64, db_column='id_transaction')
    id_block = models.IntegerField(verbose_name='ID Block', default=0, db_column='id_block')
    position = models.IntegerField(verbose_name='Position', default=0, db_column='position')
    timestamp = models.DateTimeField(verbose_name='Timestamp', auto_now=False, db_column='timestamp') 

    class Meta:
        verbose_name = 'TransactionBlock'
        verbose_name_plural = 'TransactionsBlock'
        ordering = ['timestamp']

    def __str__(self) -> str:
        return str(self.id_transaction)
    
    @staticmethod
    def check_if_exist(id: str) -> bool:
        try:
            transaction_block = TransactionBlock.objects.get(id_transaction=id)
            return True
        except TransactionBlock.DoesNotExist:
            return False
        
    @staticmethod
    def get_element_by_id(id_transaction: int):
        try:
            transaction_block = TransactionBlock.objects.get(id_transaction=id_transaction)
            return transaction_block
        except TransactionBlock.DoesNotExist:
            return None
