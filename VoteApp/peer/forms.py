from peer.models import Peer
from django.forms import ModelForm

class PeerCreateForm(ModelForm):
    class Meta:
        model = Peer
        fields = ['number', 'host', 'port', 'is_publishing_node', 'rsa_public_key', 'authorized']
