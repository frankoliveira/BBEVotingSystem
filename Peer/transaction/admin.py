from django.contrib import admin
from .models import PendingTransaction, TransactionBlock

@admin.register(PendingTransaction)
class PendingTransactionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'input', 'confirmed')

@admin.register(TransactionBlock)
class TransactionBlockModelAdmin(admin.ModelAdmin):
    list_display = ('id_transaction', 'id_block', 'position')