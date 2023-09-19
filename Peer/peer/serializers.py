from rest_framework import serializers
from peer.models import Peer

class PeerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Peer
        fields = ['host', 'port', 'name', 'is_publishing_node']
