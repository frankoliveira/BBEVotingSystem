from django.contrib import admin
from .models import Peer

@admin.register(Peer)
class PeerModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_publishing_node', 'authorized')