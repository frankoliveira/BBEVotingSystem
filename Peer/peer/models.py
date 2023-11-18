from security.CustomRSA import CustomRSA

from django.db import models
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey

class Peer(models.Model):
    #em produção o id poderia ser apenas o ip
    id = models.CharField(verbose_name='ID', primary_key=True, max_length=15, help_text="IP:PORTA", db_column='id') #id: ip:port
    host = models.CharField(verbose_name='Host', max_length=100, help_text="Endereço IP", db_column='host')
    port = models.IntegerField(verbose_name='Port', help_text="Porta", db_column='port')
    name = models.CharField(verbose_name='Name', max_length=100, help_text="Nome", db_column='name')
    is_publishing_node = models.BooleanField(verbose_name='Is publishing node', default=False, help_text="Nó completo", db_column='is_publishing_node')
    rsa_public_key = models.TextField(verbose_name='RSA Public Key', max_length=1000, help_text="Chave pública", db_column='rsa_public_key')
    authorized = models.BooleanField(verbose_name="Authorized", default=False, help_text="Autorizado", db_column='authorized')
    
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
        
    @staticmethod
    def get_publishing_peers():
        peers = Peer.objects.filter(is_publishing_node=True, authorized=True)
        if len(peers)>0:
            return peers
        return None
    
    def get_public_key(self) -> RSAPublicKey:
        return CustomRSA.load_pem_public_key_from_bytes(key=self.rsa_public_key.encode('utf-8'))