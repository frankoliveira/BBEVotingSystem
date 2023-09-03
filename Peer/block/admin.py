from django.contrib import admin
from block.models import Block

@admin.register(Block)
class BlockModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'transactions',  'timestamp', 'previous_hash', 'hash')

    fieldsets = (
        ('Header', {'fields': ('peer', 'timestamp', 'previous_hash')}),
        ('Transações', {'fields': ('transactions',)})
    )
    
    def dict(self, instance):
        return instance.as_dict()
    
    def hash(self, instance):
        return instance.hash()