from rest_framework import serializers
from transaction.models import Transaction, TransactionBlock

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'input', 'timestamp', 'origin', 'signature']

class TransactionBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionBlock
        fields = ['id_transaction', 'id_block', 'position', 'timestamp']