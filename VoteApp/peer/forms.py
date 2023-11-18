from peer.models import Peer
from django.forms import ModelForm

class PeerCreateForm(ModelForm):
    class Meta:
        model = Peer
        fields = [ 'id', 'host', 'port', 'name', 'is_publishing_node', 'rsa_public_key', 'authorized']
