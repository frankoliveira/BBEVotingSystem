from rest_framework import serializers
from transaction.models import PendingTransaction, TransactionBlock

class PendingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PendingTransaction
        fields = ['id', 'input', 'timestamp', 'signature', 'confirmed']

class TransactionBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionBlock
        fields = ['id_transaction', 'id_block', 'position', 'timestamp']