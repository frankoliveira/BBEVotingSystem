#Model
from peer.models import Peer

#Forms
from peer.forms import PeerCreateForm

#Serializer

#Django
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required

@login_required
def peer_create(request):
    if request.method == 'POST':
        peer_form = PeerCreateForm(request.POST)
        if peer_form.is_valid():
            peer = peer_form.save(commit=False)
            peer.save()
            return redirect('index')
        messages.error(request, "Erro ao criar peer")
    form = PeerCreateForm()
    return render(request=request, template_name="peer_create_form.html", context={"peer_form": form})