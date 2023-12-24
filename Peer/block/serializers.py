from rest_framework import serializers
from block.models import Block

class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'peer', 'timestamp','merkle_root', 'previous_hash', 'total_transactions', 'transactions']
