#Model
from voting.models import Election

#Forms
from voting.forms import ElectionCreateForm

#Serializer
from voting.serializers import ElectionSerializer

#Django
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view

#Other
from datetime import datetime
from hashlib import sha256
from datetime import datetime

def criar_eleicao(request):
    if request.method == 'POST':
        print(request.POST)
        election_form = ElectionCreateForm(request.POST)
        if election_form.is_valid():
            election = election_form.save(commit=False)
            election.id_author = request.user
            election.creation = datetime.now()
            election.save()
            return redirect('index')
        messages.error(request, "Erro ao criar eleição")
    form = ElectionCreateForm()
    return render(request=request, template_name="election_form.html", context={"election_form": form})

@api_view(['GET']) 
def election_list(request, format=None):
    if request.method == 'GET':
        elections = Election.objects.all()
        serialized_elections = None
        if elections:
            serializer = ElectionSerializer(instance=elections, many=True)
            serialized_elections = serializer.data
        
        return render(request=request, template_name="elections.html", context={"elections": serialized_elections})
            
def election_vote(request, pk, format=None):
    election = None
    try:
        election = Election.objects.get(id=pk)
    except Election.DoesNotExist:
        return render(request=request, template_name="election_vote.html", context={"election": None})
    
    if request.method == 'GET':
        #logged_user_id = 0
        serializer = ElectionSerializer(instance=election)
        return render(request=request, template_name="election_vote.html", context={"election": serializer.data})
