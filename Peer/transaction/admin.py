from django.contrib import admin
from .models import PendingTransaction

@admin.register(PendingTransaction)
class PendingTransactionModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'input', 'confirmed')