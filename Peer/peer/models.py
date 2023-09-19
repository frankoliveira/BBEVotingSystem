from django.db import models

class Peer(models.Model):
    host = models.CharField(verbose_name='Host', max_length=100, db_column='host') #essa é a pk
    port = models.IntegerField(verbose_name='Porta', primary_key=True, db_column='port')
    name = models.CharField(verbose_name='Name', max_length=100, db_column='name')
    is_publishing_node = models.BooleanField(verbose_name='Is publishing node', default=False, db_column='is_publishing_node')
    #rsa_public_key = models.CharField(verbose_name='RSA Public Key', max_length=200, default='', db_column='rsa_public_key')
    #is_valid = models.BooleanField(verbose_name='Is valid', default=False, db_column='is_valid')

    class Meta:
        verbose_name = 'Peer'
        verbose_name_plural = 'Peers'
        ordering = ['port']

    def __str__(self) -> str:
        return str(self.port)