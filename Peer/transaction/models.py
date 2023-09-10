from django.db import models

class Transaction(models.Model):
    id = models.CharField(verbose_name='ID', primary_key=True, max_length=64, db_column='id')
    timestamp = models.DateTimeField(verbose_name='Timestamp', auto_now=False, db_column='timestamp')
    #data = models.CharField(verbose_name='Data', max_length=500, db_column='data')
    id_block = models.IntegerField(verbose_name='ID Block', db_column='id_block')
    #confirmed = models.BooleanField(verbose_name='Confirmed', default=False, db_column='confirmed')

    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        ordering = ['timestamp']

    def __str__(self) -> str:
        return str(self.id)