from django.db import models

class Peer(models.Model):
    #em produção o id poderia ser apenas o ip
    id = models.CharField(verbose_name='ID', primary_key=True, max_length=15, db_column='id') #id: ip:port
    host = models.CharField(verbose_name='Host', max_length=100, db_column='host')
    port = models.IntegerField(verbose_name='Porta', db_column='port')
    name = models.CharField(verbose_name='Name', max_length=100, db_column='name')
    is_publishing_node = models.BooleanField(verbose_name='Is publishing node', default=False, db_column='is_publishing_node')
    #rsa_public_key = models.CharField(verbose_name='RSA Public Key', max_length=200, default='', db_column='rsa_public_key')
    #is_valid = models.BooleanField(verbose_name='Is valid', default=False, db_column='is_valid')

    class Meta:
        verbose_name = 'Peer'
        verbose_name_plural = 'Peers'
        ordering = ['id']

    def __str__(self) -> str:
        return str(self.port)
    
    @staticmethod
    def get_peer_by_id(id: int):
        try:
            peer = Peer.objects.get(id=id)
            return peer
        except Peer.DoesNotExist:
            return None