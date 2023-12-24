from rest_framework import serializers
from peer.models import Peer

class PeerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peer
        fields = ['number', 'host', 'port', 'is_publishing_node', 'rsa_public_key', 'public_address']
