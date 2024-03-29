from django.contrib import admin
from block.models import Block

@admin.register(Block)
class BlockModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'transactions',  'timestamp', 'previous_hash', 'hash')

    fieldsets = (
        ('Header', {'fields': ('peer', 'timestamp', 'merkle_root', 'previous_hash', 'total_transactions')}),
        ('Transações', {'fields': ('transactions',)})
    )
    
    def hash(self, instance):
        return instance.hash()