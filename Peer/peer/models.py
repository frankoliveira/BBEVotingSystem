from django.db import models

class Peer(models.Model):
    ip = models.CharField(verbose_name='IP', max_length=100, primary_key=True)
    port = models.IntegerField(verbose_name='Porta')
    rsa_public_key = models.CharField(verbose_name='Chave Pública', max_length=200)