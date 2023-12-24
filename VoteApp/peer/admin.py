from django.contrib import admin
from .models import Peer

@admin.register(Peer)
class PeerModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'is_publishing_node', 'authorized')