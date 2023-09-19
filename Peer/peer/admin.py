from django.contrib import admin
from .models import Peer

@admin.register(Peer)
class PeerModelAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'name', 'is_publishing_node')