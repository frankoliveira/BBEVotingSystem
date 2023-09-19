from django.db import models

class PendingTransaction(models.Model):
    '''
    Unconfirmed transactions
    '''
    id = models.CharField(verbose_name='ID', primary_key=True, max_length=64, db_column='id') #hash dos atributos abaixo
    input = models.CharField(verbose_name='Data', max_length=500, db_column='input') #voto
    timestamp = models.DateTimeField(verbose_name='Timestamp', auto_now=False, db_column='timestamp') #recebimento
    signature = models.CharField(verbose_name='ID', primary_key=True, max_length=64, db_column='signature') #peer/app e-vote
    confirmed = models.BooleanField(verbose_name='Confirmed', default=False, db_column='confirmed')
    
    class Meta:
        verbose_name = 'Pending Transaction'
        verbose_name_plural = 'Pending Transactions'
        ordering = ['id']

    def __str__(self) -> str:
        return str(self.id)
    
class TransactionBlock(models.Model):
    '''
    Confirmed transaction reference, the data is stored inside the block
    '''
    id_transaction = models.CharField(verbose_name='ID', primary_key=True, max_length=64, db_column='id_transaction')
    id_block = models.IntegerField(verbose_name='ID Block', default=0, db_column='id_block')
    position = models.IntegerField(verbose_name='ID Block', default=0, db_column='position') 